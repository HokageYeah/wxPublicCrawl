# -*- coding:utf-8 -*-
"""
下载管理器 - 实现断点续传和速率限制处理
"""
import asyncio
import json
import os
import time
from datetime import datetime, timedelta
import aiofiles
import aiohttp
import colorama
import logging
from typing import Dict, List, Optional
from app.utils.src_path import get_xmly_download_path

logger = logging.getLogger('logger')
colorama.init(autoreset=True)


class DownloadManager:
    """管理专辑下载流程,支持断点续传和速率限制"""

    def __init__(self, base_path: str = ""):
        self.base_path = base_path if base_path else get_xmly_download_path()
        self.rate_limit_errors = ["系统繁忙", "请求过于频繁", "Too Many Requests"]
        self.global_status_file = os.path.join(base_path, "albums_status.json")

    def _get_album_cache_path(self, album_name: str) -> str:
        """获取专辑缓存目录路径"""
        safe_name = self._replace_invalid_chars(album_name)
        return os.path.join(self.base_path, safe_name)

    def _get_album_info_path(self, album_name: str) -> str:
        """获取专辑信息JSON文件路径"""
        cache_path = self._get_album_cache_path(album_name)
        return os.path.join(cache_path, "album_info.json")

    def _get_progress_path(self, album_name: str) -> str:
        """获取下载进度JSON文件路径"""
        cache_path = self._get_album_cache_path(album_name)
        return os.path.join(cache_path, "download_progress.json")

    def _get_metadata_path(self, album_name: str) -> str:
        """获取metadata.json文件路径"""
        cache_path = self._get_album_cache_path(album_name)
        return os.path.join(cache_path, "metadata.json")

    def _replace_invalid_chars(self, name: str) -> str:
        """替换文件名中的非法字符"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                name = name.replace(char, " ")
        return name

    async def _load_global_status(self) -> Dict:
        """加载全局专辑状态记录"""
        if not os.path.exists(self.global_status_file):
            return {}

        async with aiofiles.open(self.global_status_file, mode="r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

    async def _save_global_status(self, status_data: Dict):
        """保存全局专辑状态记录"""
        os.makedirs(self.base_path, exist_ok=True)
        async with aiofiles.open(self.global_status_file, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(status_data, ensure_ascii=False, indent=2))

    async def get_album_status(self, album_id: int) -> Optional[str]:
        """
        获取专辑处理状态

        Args:
            album_id: 专辑ID

        Returns:
            str: 'pending' | 'processing' | 'completed' | 'failed' | None(未记录)
        """
        status_data = await self._load_global_status()
        album_key = str(album_id)
        if album_key in status_data:
            return status_data[album_key].get("status")
        return None

    async def update_album_status(self, album_id: int, album_name: str, status: str,
                                  total_count: int = 0, success_count: int = 0):
        """
        更新专辑处理状态

        Args:
            album_id: 专辑ID
            album_name: 专辑名称
            status: 状态 'pending' | 'processing' | 'completed' | 'failed'
            total_count: 总音频数
            success_count: 成功下载数
        """
        status_data = await self._load_global_status()
        album_key = str(album_id)

        status_data[album_key] = {
            "album_id": album_id,
            "album_name": album_name,
            "status": status,
            "total_count": total_count,
            "success_count": success_count,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cache_path": self._get_album_cache_path(album_name)
        }

        await self._save_global_status(status_data)
        logger.info(f"专辑 {album_id} 状态更新为: {status}")

    async def get_album_info_by_id(self, album_id: int) -> Optional[Dict]:
        """
        通过专辑ID获取已缓存的专辑信息

        Args:
            album_id: 专辑ID

        Returns:
            Dict: 专辑信息,如果不存在返回None
        """
        status_data = await self._load_global_status()
        album_key = str(album_id)

        if album_key not in status_data:
            return None

        # 获取缓存路径
        album_name = status_data[album_key]["album_name"]
        info_path = self._get_album_info_path(album_name)

        if not os.path.exists(info_path):
            return None

        async with aiofiles.open(info_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

    async def list_all_albums(self) -> List[Dict]:
        """
        列出所有已记录的专辑

        Returns:
            List[Dict]: 专辑列表
        """
        status_data = await self._load_global_status()
        return [
            {
                "album_id": info["album_id"],
                "album_name": info["album_name"],
                "status": info["status"],
                "progress": f"{info['success_count']}/{info['total_count']}",
                "last_update": info["last_update"]
            }
            for info in status_data.values()
        ]

    async def save_album_info(self, album_id: int, album_name: str,
                              album_cover: str, sounds: List[Dict],
                              resource_type: str):
        """
        保存专辑解析结果到JSON文件，支持增量更新

        Args:
            album_id: 专辑ID
            album_name: 专辑名称
            album_cover: 专辑封面URL
            sounds: 音频列表(来自analyze_album的结果)
            resource_type: 资源类型(歌曲/故事)
        """
        cache_path = self._get_album_cache_path(album_name)
        logger.info(f"专辑缓存目录路径: {cache_path}")
        logger.info(f"专辑信息sounds: {sounds}")
        os.makedirs(cache_path, exist_ok=True)

        # 检查是否已存在专辑信息
        existing_info = await self.get_album_info_by_id(album_id)
        existing_sounds = []

        if existing_info:
            # 获取已存在的sounds列表
            existing_sounds = existing_info.get("sounds", [])
            existing_track_ids = {str(s.get("trackId")) for s in existing_sounds}
            logger.info(f"已存在专辑信息，现有曲目数: {len(existing_sounds)}")

            # 合并sounds，只添加新的曲目
            merged_sounds = existing_sounds.copy()
            new_sounds = []

            for sound in sounds:
                track_id = str(sound.get("trackId"))
                if track_id not in existing_track_ids:
                    merged_sounds.append(sound)
                    new_sounds.append(sound)
                    logger.info(f"新增曲目: {track_id} - {sound.get('title', '')}")

            sounds = merged_sounds
            logger.info(f"合并后总曲目数: {len(sounds)}，新增曲目数: {len(new_sounds)}")
        else:
            logger.info(f"新建专辑信息，曲目数: {len(sounds)}")

        album_info = {
            "album_id": album_id,
            "album_name": album_name,
            "album_cover": album_cover,
            "resource_type": resource_type,
            "total_count": len(sounds),
            "parsed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sounds": sounds
        }

        info_path = self._get_album_info_path(album_name)
        async with aiofiles.open(info_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(album_info, ensure_ascii=False, indent=2))

        print(colorama.Fore.GREEN + f"✓ 专辑信息已保存: {info_path}")
        logger.info(f"专辑 {album_name} 信息已保存")

        # 更新全局状态为 processing
        await self.update_album_status(
            album_id, album_name, "processing",
            total_count=len(sounds), success_count=0
        )

        # 初始化或更新下载进度文件
        await self._init_or_update_progress(album_name, sounds)

    async def _init_progress(self, album_name: str, sounds: List[Dict]):
        """初始化下载进度记录"""
        progress_path = self._get_progress_path(album_name)

        # 如果进度文件已存在,不覆盖
        if os.path.exists(progress_path):
            print(colorama.Fore.YELLOW + f"⚠ 检测到已有下载进度,将从断点继续")
            return

        progress = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_count": len(sounds),
            "success_count": 0,
            "failed_count": 0,
            "downloads": {}
        }

        # 为每个音频初始化状态
        for sound in sounds:
            track_id = str(sound.get("trackId"))
            progress["downloads"][track_id] = {
                "status": "pending",  # pending, success, failed
                "title": sound.get("title", ""),
                "retry_count": 0,
                "last_attempt": None,
                "error_message": None
            }

        async with aiofiles.open(progress_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(progress, ensure_ascii=False, indent=2))

        print(colorama.Fore.GREEN + f"✓ 下载进度文件已初始化: {progress_path}")

    async def _init_or_update_progress(self, album_name: str, sounds: List[Dict]):
        """
        初始化或更新下载进度记录，支持增量更新

        Args:
            album_name: 专辑名称
            sounds: 音频列表
        """
        progress_path = self._get_progress_path(album_name)

        # 检查进度文件是否已存在
        if os.path.exists(progress_path):
            # 加载现有进度
            async with aiofiles.open(progress_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                progress = json.loads(content)

            print(colorama.Fore.YELLOW + f"⚠ 检测到已有下载进度，准备合并...")

            # 获取现有的track IDs
            existing_track_ids = set(progress["downloads"].keys())

            # 只添加新的曲目到进度中
            new_count = 0
            for sound in sounds:
                track_id = str(sound.get("trackId"))
                if track_id not in existing_track_ids:
                    progress["downloads"][track_id] = {
                        "status": "pending",
                        "title": sound.get("title", ""),
                        "retry_count": 0,
                        "last_attempt": None,
                        "error_message": None
                    }
                    new_count += 1
                    logger.info(f"新增曲目到进度文件: {track_id} - {sound.get('title', '')}")

            # 更新总数
            progress["total_count"] = len(sounds)
            progress["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 保存更新后的进度
            async with aiofiles.open(progress_path, mode="w", encoding="utf-8") as f:
                await f.write(json.dumps(progress, ensure_ascii=False, indent=2))

            print(colorama.Fore.GREEN + f"✓ 下载进度文件已更新，新增 {new_count} 个曲目")
            logger.info(f"下载进度文件已更新，新增 {new_count} 个曲目")
        else:
            # 首次初始化进度文件
            await self._init_progress(album_name, sounds)

    async def load_album_info(self, album_name: str) -> Optional[Dict]:
        """加载专辑信息"""
        info_path = self._get_album_info_path(album_name)
        if not os.path.exists(info_path):
            return None

        async with aiofiles.open(info_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

    async def load_progress(self, album_name: str) -> Optional[Dict]:
        """加载下载进度"""
        progress_path = self._get_progress_path(album_name)
        if not os.path.exists(progress_path):
            return None

        async with aiofiles.open(progress_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

    async def update_download_status(self, album_name: str, track_id: str,
                                    status: str, error_message: Optional[str] = None,
                                    album_id: Optional[int] = None):
        """
        更新单个音频的下载状态

        Args:
            album_name: 专辑名称
            track_id: 音频ID
            status: 状态(success/failed/pending)
            error_message: 错误信息(可选)
            album_id: 专辑ID(可选,用于更新全局状态)
        """
        progress = await self.load_progress(album_name)
        if not progress:
            return

        track_id = str(track_id)
        if track_id in progress["downloads"]:
            old_status = progress["downloads"][track_id]["status"]
            progress["downloads"][track_id]["status"] = status
            progress["downloads"][track_id]["last_attempt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if error_message:
                progress["downloads"][track_id]["error_message"] = error_message

            # 更新重试计数
            if status == "failed":
                progress["downloads"][track_id]["retry_count"] += 1

            # 更新统计
            if old_status != "success" and status == "success":
                progress["success_count"] += 1
            elif old_status != "failed" and status == "failed":
                progress["failed_count"] += 1

            progress["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 保存进度
            progress_path = self._get_progress_path(album_name)
            async with aiofiles.open(progress_path, mode="w", encoding="utf-8") as f:
                await f.write(json.dumps(progress, ensure_ascii=False, indent=2))

            # 更新全局状态
            if album_id:
                await self.update_album_status(
                    album_id, album_name,
                    "processing",
                    total_count=progress["total_count"],
                    success_count=progress["success_count"]
                )

    async def append_to_metadata(self, album_name: str, track_info: Dict):
        """
        将成功下载的音频信息追加到metadata.json

        Args:
            album_name: 专辑名称
            track_info: 音频信息
        """
        metadata_path = self._get_metadata_path(album_name)

        # 读取现有metadata
        if os.path.exists(metadata_path):
            async with aiofiles.open(metadata_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                metadata = json.loads(content)
        else:
            # 首次创建metadata
            album_info = await self.load_album_info(album_name)
            metadata = {
                "album_name": album_name,
                "album_id": album_info["album_id"],
                "cover_url": album_info["album_cover"],
                "resource_type": album_info["resource_type"],
                "download_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": album_info["total_count"],
                "success_count": 0,
                "resources": []
            }

        # 检查是否已存在该track_id
        existing_ids = {r["track_id"] for r in metadata["resources"]}
        if track_info["track_id"] not in existing_ids:
            metadata["resources"].append(track_info)
            metadata["success_count"] = len(metadata["resources"])

        # 保存metadata
        async with aiofiles.open(metadata_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(metadata, ensure_ascii=False, indent=2))

    def is_rate_limited(self, error_message: str) -> bool:
        """检测是否触发速率限制"""
        if not error_message:
            return False
        return any(keyword in error_message for keyword in self.rate_limit_errors)

    async def wait_until_next_hour(self):
        """等待到下个小时的起点"""
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        wait_seconds = (next_hour - now).total_seconds()

        print(colorama.Fore.YELLOW + f"\n⏳ 检测到速率限制,将等待到下个小时 {next_hour.strftime('%H:%M:%S')}")
        print(colorama.Fore.YELLOW + f"⏳ 等待时间: {int(wait_seconds // 60)} 分 {int(wait_seconds % 60)} 秒")

        # 显示倒计时
        while wait_seconds > 0:
            mins, secs = divmod(int(wait_seconds), 60)
            timer = f"{mins:02d}:{secs:02d}"
            print(f"\r⏳ 剩余时间: {timer}", end="", flush=True)
            await asyncio.sleep(1)
            wait_seconds -= 1

        print(colorama.Fore.GREEN + f"\n✓ 等待结束,继续下载...")

    async def wait_until_next_minute(self, minutes: int = 2):
        """
        等待到下一个指定分钟数的起点

        Args:
            minutes: 分钟间隔，默认2分钟
        """
        now = datetime.now()
        current_minute = now.minute
        current_second = now.second

        # 计算下一个目标分钟数
        next_minute = ((current_minute // minutes) + 1) * minutes

        # 如果超过60分钟，进入下个小时
        if next_minute >= 60:
            next_hour = now.hour + 1
            next_minute = next_minute - 60
        else:
            next_hour = now.hour

        # 构建目标时间
        next_time = now.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)

        # 如果计算出的目标时间小于当前时间，说明需要进入下一个周期
        if next_time <= now:
            next_time = next_time + timedelta(minutes=minutes)

        wait_seconds = (next_time - now).total_seconds()

        print(colorama.Fore.YELLOW + f"\n⏳ 检测到速率限制,将等待到下一个{minutes}分钟节点 {next_time.strftime('%H:%M:%S')}")
        print(colorama.Fore.YELLOW + f"⏳ 等待时间: {int(wait_seconds // 60)} 分 {int(wait_seconds % 60)} 秒")

        # 显示倒计时
        while wait_seconds > 0:
            mins, secs = divmod(int(wait_seconds), 60)
            timer = f"{mins:02d}:{secs:02d}"
            print(f"\r⏳ 剩余时间: {timer}", end="", flush=True)
            await asyncio.sleep(1)
            wait_seconds -= 1

        print(colorama.Fore.GREEN + f"\n✓ 等待结束,继续下载...")

    def get_pending_downloads(self, progress: Dict) -> List[str]:
        """获取待下载的音频ID列表"""
        pending = []
        for track_id, info in progress["downloads"].items():
            if info["status"] == "pending" or (info["status"] == "failed" and info["retry_count"] < 3):
                pending.append(track_id)
        return pending

    def is_album_complete(self, progress: Dict) -> bool:
        """检查专辑是否全部下载完成"""
        total = progress["total_count"]
        success = progress["success_count"]

        # 检查是否还有可重试的失败项
        retriable_failed = sum(
            1 for info in progress["downloads"].values()
            if info["status"] == "failed" and info["retry_count"] < 3
        )

        return success == total or (success + retriable_failed == 0)

    def get_download_summary(self, progress: Dict) -> str:
        """生成下载摘要信息"""
        total = progress["total_count"]
        success = progress["success_count"]
        failed = progress["failed_count"]
        pending = total - success - failed

        summary = f"\n{'='*50}\n"
        summary += f"📊 下载统计:\n"
        summary += f"  总计: {total} 个\n"
        summary += f"  ✓ 成功: {success} 个\n"
        summary += f"  ✗ 失败: {failed} 个\n"
        summary += f"  ⏳ 待下载: {pending} 个\n"
        summary += f"  完成率: {success/total*100:.1f}%\n"
        summary += f"{'='*50}\n"

        return summary
