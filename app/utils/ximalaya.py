# -*- coding:utf-8 -*-
import asyncio
import base64
import binascii
import json
import math
import os
import re
import time
import logging
import traceback

import aiofiles
import aiohttp
import requests
from datetime import datetime
from Crypto.Cipher import AES
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import colorama
from asyncio import Lock
from src.utils.sign_generator import XimalayaSignNode
from src.utils.slider_solver import SliderSolver
from src.core.download_manager import DownloadManager

sign_generator = XimalayaSignNode()
slider_solver = SliderSolver(headless=True)  # 滑块验证解决器（Docker环境必须使用headless模式）
colorama.init(autoreset=True)
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log', mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
path = ""

lock = Lock()

class Ximalaya:
    def __init__(self):
        self.default_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "Xm-Sign": sign_generator.get_xm_sign()
        }
        self.cookies = None  # 存储验证后的cookies
        self.search_url = "https://www.ximalaya.com/revision/search/main"
        self.need_slider_verification = False  # 是否需要滑块验证
        self.download_manager = DownloadManager()  # 下载管理器

    # 解析声音，如果成功返回声音名和声音链接，否则返回False
    def analyze_sound(self, sound_id, headers):
        logger.debug(f'开始解析ID为{sound_id}的声音')
        url = f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}"
        params = {
            "device": "web",
            "trackId": sound_id,
            "trackQualityLevel": 2
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            print(response.json())
        except Exception as e:
            print(colorama.Fore.RED + f'ID为{sound_id}的声音解析失败！')
            logger.debug(f'ID为{sound_id}的声音解析失败！')
            logger.debug(traceback.format_exc())
            return False
        if not response.json()["trackInfo"]["isAuthorized"]:
            return 0  # 未购买或未登录vip账号
        try:
            sound_name = response.json()["trackInfo"]["title"]
            encrypted_url_list = response.json()["trackInfo"]["playUrlList"]
        except Exception as e:
            print(colorama.Fore.RED + f'ID为{sound_id}的声音解析失败！')
            logger.debug(f'ID为{sound_id}的声音解析失败！')
            logger.debug(traceback.format_exc())
            return False
        sound_info = {"name": sound_name, 0: "", 1: "", 2: ""}
        for encrypted_url in encrypted_url_list:
            if encrypted_url["type"] == "M4A_128":
                sound_info[2] = self.decrypt_url(encrypted_url["url"])
            elif encrypted_url["type"] == "MP3_64":
                sound_info[1] = self.decrypt_url(encrypted_url["url"])
            elif encrypted_url["type"] == "MP3_32":
                sound_info[0] = self.decrypt_url(encrypted_url["url"])
        logger.debug(f'ID为{sound_id}的声音解析成功！')
        return sound_info

    def get_album_parse_progress_file(self, album_id):
        """获取专辑解析进度文件路径"""
        return f"download/album_{album_id}_parse_progress.json"

    def load_album_parse_progress(self, album_id):
        """加载专辑解析进度"""
        progress_file = self.get_album_parse_progress_file(album_id)
        if not os.path.exists(progress_file):
            return None

        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载解析进度失败: {str(e)}")
            return None

    def save_album_parse_progress(self, album_id, progress_data):
        """保存专辑解析进度"""
        os.makedirs("download", exist_ok=True)
        progress_file = self.get_album_parse_progress_file(album_id)

        try:
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存解析进度失败: {str(e)}")

    def delete_album_parse_progress(self, album_id):
        """删除专辑解析进度文件（解析完成后）"""
        progress_file = self.get_album_parse_progress_file(album_id)
        if os.path.exists(progress_file):
            try:
                os.remove(progress_file)
            except Exception as e:
                logger.error(f"删除解析进度文件失败: {str(e)}")

    # 解析专辑，如果成功返回专辑名和专辑声音列表，否则返回False
    async def analyze_album(self, album_id):
        logger.debug(f'开始解析ID为{album_id}的专辑')
        url = "https://www.ximalaya.com/revision/album/v1/getTracksList"

        # 1. 尝试加载解析进度
        parse_progress = self.load_album_parse_progress(album_id)
        if parse_progress:
            print(colorama.Fore.CYAN + f"✓ 检测到专辑 {album_id} 的解析进度")
            print(f"  已解析页数: {parse_progress['completed_pages']}/{parse_progress['total_pages']}")
            print(f"  已获取音频: {len(parse_progress['sounds'])} 个")
            print(colorama.Fore.YELLOW + "  继续从断点恢复解析...")

            sounds = parse_progress['sounds']
            album_name = parse_progress.get('album_name')
            completed_pages = parse_progress['completed_pages']
            total_pages = parse_progress['total_pages']
            start_page = completed_pages + 1
        else:
            sounds = []
            album_name = None
            start_page = 1
            total_pages = None

        # 2. 首先尝试加载已保存的cookies
        if self.cookies is None:
            loaded_cookies = slider_solver.load_cookies()
            if loaded_cookies:
                print(colorama.Fore.CYAN + "已加载缓存的cookies")
                self.cookies = loaded_cookies

        # 3. 准备请求头
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "Xm-Sign": sign_generator.get_xm_sign()
        }

        if self.cookies:
            headers['Cookie'] = slider_solver.get_cookies_string(self.cookies)

        # 4. 如果是新解析，先获取专辑基本信息
        if total_pages is None:
            params = {
                "albumId": album_id,
                "pageNum": 1,
                "pageSize": 5
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=15)
                response_data = response.json()
                print(response_data)

                # 检查是否触发滑块验证
                if response_data.get('ret') == 200:
                    risk_level = response_data.get('data', {}).get('riskLevel', 0)
                    tracks = response_data.get('data', {}).get('tracks', [])

                    # riskLevel=5 或 tracks为空表示需要滑块验证
                    if risk_level == 5 or len(tracks) == 0:
                        print(colorama.Fore.YELLOW + f'\n检测到风险等级: {risk_level}，需要滑块验证')
                        print(colorama.Fore.YELLOW + '正在启动滑块验证流程...\n')

                        # 执行滑块验证
                        album_url = f"https://www.ximalaya.com/album/{album_id}"
                        self.cookies = await slider_solver.solve_slider(album_url)

                        # 使用新cookies重试
                        headers['Cookie'] = slider_solver.get_cookies_string(self.cookies)
                        response = requests.get(url, headers=headers, params=params, timeout=15)
                        response_data = response.json()
                        print(colorama.Fore.GREEN + "\n使用新cookies重新请求:")

            except Exception as e:
                print(colorama.Fore.RED + f'ID为{album_id}的专辑解析失败！')
                logger.debug(f'ID为{album_id}的专辑解析失败！')
                logger.debug(traceback.format_exc())
                return False, False

            # 获取总页数
            track_count = response_data.get("data", {}).get("trackTotalCount", 0)
            if track_count == 0:
                print(colorama.Fore.RED + '未能获取到专辑数据，可能仍需要验证')
                return False, False

            total_pages = math.ceil(track_count / 99)
            print(colorama.Fore.CYAN + f"专辑总音频数: {track_count}，共 {total_pages} 页")

        # 5. 分页获取所有音频（从断点继续）
        for page in range(start_page, total_pages + 1):
            print(colorama.Fore.CYAN + f"⏳ 正在解析第 {page}/{total_pages} 页...")

            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
                "Xm-Sign": sign_generator.get_xm_sign()
            }

            if self.cookies:
                headers['Cookie'] = slider_solver.get_cookies_string(self.cookies)

            params = {
                "albumId": album_id,
                "pageNum": page,
                "pageSize": 99
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                page_data = response.json()

                # 检查是否触发滑块验证
                if page_data.get('ret') == 200:
                    risk_level = page_data.get('data', {}).get('riskLevel', 0)
                    tracks = page_data.get('data', {}).get('tracks', [])

                    # riskLevel=5 或 tracks为空表示需要滑块验证
                    if risk_level == 5 or len(tracks) == 0:
                        print(colorama.Fore.YELLOW + f'\n第{page}页检测到风险等级: {risk_level}，需要滑块验证')
                        print(colorama.Fore.YELLOW + '正在启动滑块验证流程...\n')

                        # 执行滑块验证
                        album_url = f"https://www.ximalaya.com/album/{album_id}"
                        self.cookies = await slider_solver.solve_slider(album_url)

                        # 使用新cookies重试
                        headers['Cookie'] = slider_solver.get_cookies_string(self.cookies)
                        response = requests.get(url, headers=headers, params=params, timeout=15)
                        page_data = response.json()
                        print(colorama.Fore.GREEN + "\n使用新cookies重新请求:")

                if page_data.get('ret') == 200:
                    page_tracks = page_data.get("data", {}).get("tracks", [])
                    sounds += page_tracks

                    # 获取专辑名称（从第一页的数据中）
                    if album_name is None and len(page_tracks) > 0:
                        album_name = page_tracks[0]["albumTitle"]

                    # 保存进度
                    progress_data = {
                        "album_id": album_id,
                        "album_name": album_name,
                        "total_pages": total_pages,
                        "completed_pages": page,
                        "sounds": sounds,
                        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.save_album_parse_progress(album_id, progress_data)

                    print(colorama.Fore.GREEN + f"✓ 第 {page}/{total_pages} 页解析完成，已获取 {len(page_tracks)} 个音频")
                else:
                    raise Exception(f"API返回错误: {page_data.get('msg', '未知错误')}")

            except Exception as e:
                print(colorama.Fore.RED + f'✗ ID为{album_id}的专辑第{page}页解析失败！')
                print(colorama.Fore.YELLOW + f'⚠ 已保存进度，当前已成功解析 {page-1}/{total_pages} 页')
                logger.error(f'ID为{album_id}的专辑第{page}页解析失败: {str(e)}')
                logger.debug(traceback.format_exc())

                # 保存当前进度（标记为失败状态）
                if len(sounds) > 0:
                    progress_data = {
                        "album_id": album_id,
                        "album_name": album_name,
                        "total_pages": total_pages,
                        "completed_pages": page - 1,
                        "sounds": sounds,
                        "last_error": str(e),
                        "failed_page": page,
                        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.save_album_parse_progress(album_id, progress_data)
                    print(colorama.Fore.CYAN + "💾 进度已保存，可以稍后重试")

                return False, False

        # 6. 解析完成
        if len(sounds) == 0:
            print(colorama.Fore.RED + '✗ 未获取到任何音频数据')
            return False, False

        # 删除进度文件
        self.delete_album_parse_progress(album_id)

        print(colorama.Fore.GREEN + f"✓ 专辑解析完成！共获取 {len(sounds)} 个音频")
        logger.debug(f'ID为{album_id}的专辑解析成功')
        return album_name, sounds

    # 协程解析声音
    async def async_analyze_sound(self, sound_id, session, headers):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            # "cookie": self.analyze_config()[0],
            "Xm-Sign": sign_generator.get_xm_sign()
        }
        url = f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}"
        params = {
            "device": "web",
            "trackId": sound_id,
            "trackQualityLevel": 2
        }
        try:
            async with session.get(url, headers=headers, params=params, timeout=60) as response:
                response_json = json.loads(await response.text())
                print(response_json)
                sound_name = response_json["trackInfo"]["title"]
                intro = response_json["trackInfo"].get("intro", "")
                trackId = response_json["trackInfo"]["trackId"]
                cover_url = response_json["trackInfo"]["coverSmall"] or ""
                encrypted_url_list = response_json["trackInfo"]["playUrlList"]
        except Exception as e:
            print(colorama.Fore.RED + f'ID为{sound_id}的声音解析失败！')
            logger.debug(f'ID为{sound_id}的声音解析失败！')
            logger.debug(traceback.format_exc())
            return False
        # if not response_json["trackInfo"]["isAuthorized"]:
        #     return 0  # 未购买或未登录vip账号
        sound_info = {
            "name": sound_name, 
            "intro": intro, 
            "trackId": trackId,
            "coverSmall": cover_url,
            0: "", 
            1: "", 
            2: ""
        }
        for encrypted_url in encrypted_url_list:
            if encrypted_url["type"] == "M4A_128" or encrypted_url["type"] == "M4A_64":
                sound_info[2] = self.decrypt_url(encrypted_url["url"])
            elif encrypted_url["type"] == "MP3_64":
                sound_info[1] = self.decrypt_url(encrypted_url["url"])
            elif encrypted_url["type"] == "MP3_32":
                sound_info[0] = self.decrypt_url(encrypted_url["url"])
        logger.info(f'ID为{sound_id}的声音解析成功！')
        return sound_info

    # 将文件名中不能包含的字符替换为空格
    def replace_invalid_chars(self, name):
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                name = name.replace(char, " ")
        return name

    # 下载单个声音
    def get_sound(self, sound_name, sound_url, path):
        retries = 3
        sound_name = self.replace_invalid_chars(sound_name)
        if '?' in sound_url:
            type = sound_url.split('?')[0][-3:]
        else:
            type = sound_url[-3:]
        if os.path.exists(f"{path}/{sound_name}.{type}"):
            print(f'{sound_name}已存在！')
            return
        while retries > 0:
            try:
                logger.debug(f'开始下载声音{sound_name}')
                response = requests.get(sound_url, headers=self.default_headers, timeout=60)
                break
            except Exception as e:
                logger.debug(f'{sound_name}第{4 - retries}次下载失败！')
                logger.debug(traceback.format_exc())
                retries -= 1
        if retries == 0:
            print(colorama.Fore.RED + f'{sound_name}下载失败！')
            logger.debug(f'{sound_name}经过三次重试后下载失败！')
            return False
        sound_file = response.content
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f"{path}/{sound_name}.{type}", mode="wb") as f:
            f.write(sound_file)
        print(f'{sound_name}下载完成！')
        logger.debug(f'{sound_name}下载完成！')

    async def async_get_sound(self, sound_name, sound_url, album_name, session, path, num=None):
        async with lock:
            await self.async_get_sound2(sound_name, sound_url, album_name, session, path, num)

    # 协程下载声音
    async def async_get_sound2(self, sound_name, sound_url, album_name, session, path, num=None):
        retries = 3
        logger.debug(f'开始下载声音{sound_name}')
        if num is None:
            sound_name = self.replace_invalid_chars(sound_name)
        else:
            sound_name = f"{num}-{sound_name}"
            sound_name = self.replace_invalid_chars(sound_name)
        if '?' in sound_url:
            type = sound_url.split('?')[0][-3:]
        else:
            type = sound_url[-3:]
        album_name = self.replace_invalid_chars(album_name)
        if not os.path.exists(f"{path}/{album_name}"):
            os.makedirs(f"{path}/{album_name}")
        if os.path.exists(f"{path}/{album_name}/{sound_name}.{type}"):
            print(f'{sound_name}已存在！')
        while retries > 0:
            try:
                async with session.get(sound_url, headers=self.default_headers, timeout=120) as response:
                    async with aiofiles.open(f"{path}/{album_name}/{sound_name}.{type}", mode="wb") as f:
                        await f.write(await response.content.read())
                print(f'{sound_name}下载完成！')
                logger.debug(f'{sound_name}下载完成！')
                break
            except Exception as e:
                logger.debug(f'{sound_name}第{4 - retries}次下载失败！')
                logger.debug(traceback.format_exc())
                retries -= 1
        if retries == 0:
            print(colorama.Fore.RED + f'{sound_name}下载失败！')
            logger.debug(f'{sound_name}经过三次重试后下载失败！')

    # 下载专辑中的选定声音
    async def get_selected_sounds(self, sounds, album_id, album_name, headers, quality, path, type):
        tasks = []
        session = aiohttp.ClientSession()
        sounds_info = []
        for i in range(len(sounds)):
            sound_id = sounds[i]["trackId"]
            dict_info = await self.async_analyze_sound(sound_id, session, headers)
            print(dict_info)
            sounds_info.append(dict_info)
        tasks = []
        downloaded_resources = []
        album_cover = sounds[0]["albumCoverPath"]
        for sound_info in sounds:
            flag = 1
            for sound in sounds_info:
                track_id = sound["trackId"]
                if sound_info.get("trackId") == track_id:
                    flag = 0
                    sound_info["intro"] = sound["intro"]
                    sound_info["name"] = sound["name"]
                    sound_info[0] = sound[0]
                    sound_info[1] = sound[1]
                    sound_info[2] = sound[2]
                    sound_info["coverSmall"] = sound["coverSmall"]
            if flag:
                continue
            title = sound_info.get("name")
            process_name = self.replace_invalid_chars(album_name)
            process_title = self.replace_invalid_chars(title)
            local_path = f"download/{process_name}/{process_title}.mp3"
            downloaded_resources.append({
                "track_id": sound_info.get("trackId", ""),
                "title": sound_info.get("title", ""),
                "cover_url": sound_info.get("coverSmall", ""),
                "local_path": local_path,
                "author": sound_info.get("anchorName", ""),
                "duration": sound_info.get("duration", 0),
                "intro": sound_info.get("intro", "")
            })
            if sound_info is False or sound_info == 0:
                continue
            if quality == 2 and sound_info[2] == "":
                quality = 1
            tasks.append(asyncio.create_task(self.async_get_sound(sound_info["name"], sound_info[quality], album_name, session, path)))

        # 只有在有任务时才等待
        if tasks:
            await asyncio.wait(tasks)
            json_data = {
                "album_name": album_name,
                "album_id": album_id,
                "cover_url": album_cover,
                "resource_type": type,
                "download_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": len(sounds),
                "success_count": len(downloaded_resources),
                "resources": downloaded_resources,
            }
            download_path = f"download/{process_name}"
            os.makedirs(download_path, exist_ok=True)

            json_file_path = os.path.join(download_path, "metadata.json")
            async with aiofiles.open(json_file_path, mode="w", encoding="utf-8") as f:
                await f.write(json.dumps(json_data, ensure_ascii=False, indent=2))
            print("专辑全部选定声音下载完成！")
        else:
            print("没有可下载的音频（可能都是VIP或未购买）")

        await session.close()

    # 增量下载专辑音频 - 支持断点续传和速率限制
    async def download_album_incremental(self, sounds, album_id, album_name, headers, quality, path, resource_type):
        """
        增量下载专辑音频,支持断点续传和速率限制处理

        Args:
            sounds: 专辑音频列表(来自analyze_album)
            album_id: 专辑ID
            album_name: 专辑名称
            headers: 请求头
            quality: 音质(0/1/2)
            path: 下载路径
            resource_type: 资源类型(歌曲/故事)
        """
        album_cover = sounds[0].get("albumCoverPath", "")

        # 1. 保存专辑解析结果
        await self.download_manager.save_album_info(
            album_id, album_name, album_cover, sounds, resource_type
        )

        # 2. 加载下载进度
        progress = await self.download_manager.load_progress(album_name)
        if not progress:
            print(colorama.Fore.RED + "无法加载下载进度文件")
            return

        # 3. 显示当前进度
        print(self.download_manager.get_download_summary(progress))

        # 4. 获取待下载列表
        pending_ids = self.download_manager.get_pending_downloads(progress)
        if not pending_ids:
            print(colorama.Fore.GREEN + "✓ 所有音频已下载完成!")
            return

        print(colorama.Fore.CYAN + f"开始下载 {len(pending_ids)} 个音频...")

        # 5. 创建会话
        session = aiohttp.ClientSession()

        # 6. 逐个下载音频
        for idx, track_id in enumerate(pending_ids, 1):
            # 查找对应的sound信息
            sound = next((s for s in sounds if str(s.get("trackId")) == track_id), None)
            if not sound:
                continue

            print(colorama.Fore.CYAN + f"\n[{idx}/{len(pending_ids)}] 处理音频: {sound.get('title', 'Unknown')}")

            try:
                # 6.1 解析音频详情(获取下载URL)
                sound_info = await self.async_analyze_sound(sound["trackId"], session, headers)

                # 检测是否触发速率限制
                if sound_info is False:
                    error_msg = "系统繁忙"
                    if self.download_manager.is_rate_limited(error_msg):
                        print(colorama.Fore.YELLOW + "⚠ 触发速率限制")
                        await self.download_manager.wait_until_next_hour()
                        # 重试当前音频
                        sound_info = await self.async_analyze_sound(sound["trackId"], session, headers)

                if sound_info is False or sound_info == 0:
                    await self.download_manager.update_download_status(
                        album_name, track_id, "failed", "解析失败或未授权", album_id
                    )
                    continue

                # 6.2 下载音频文件
                sound_url = sound_info.get(quality, "")
                if not sound_url and quality == 2:
                    sound_url = sound_info.get(1, "")  # 降级到中等音质

                if not sound_url:
                    await self.download_manager.update_download_status(
                        album_name, track_id, "failed", "无可用下载链接", album_id
                    )
                    continue

                # 执行下载
                download_success = await self._download_single_audio(
                    sound_info["name"], sound_url, album_name, session, path
                )

                if download_success:
                    # 6.3 下载成功 - 更新进度并写入metadata
                    await self.download_manager.update_download_status(
                        album_name, track_id, "success", None, album_id
                    )

                    # 构建metadata条目
                    process_name = self.replace_invalid_chars(album_name)
                    process_title = self.replace_invalid_chars(sound_info["name"])
                    local_path = f"download/{process_name}/{process_title}.mp3"

                    track_metadata = {
                        "track_id": str(sound_info.get("trackId", "")),
                        "title": sound_info.get("name", ""),
                        "cover_url": sound_info.get("coverSmall", ""),
                        "local_path": local_path,
                        "author": sound.get("anchorName", ""),
                        "duration": sound.get("duration", 0),
                        "intro": sound_info.get("intro", "")
                    }

                    # 追加到metadata.json
                    await self.download_manager.append_to_metadata(album_name, track_metadata)

                    print(colorama.Fore.GREEN + f"✓ [{idx}/{len(pending_ids)}] 下载成功: {sound_info['name']}")
                else:
                    # 下载失败
                    await self.download_manager.update_download_status(
                        album_name, track_id, "failed", "下载文件失败", album_id
                    )
                    print(colorama.Fore.RED + f"✗ [{idx}/{len(pending_ids)}] 下载失败: {sound_info['name']}")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"下载音频 {track_id} 时出错: {error_msg}")
                logger.error(traceback.format_exc())

                # 检测速率限制
                if self.download_manager.is_rate_limited(error_msg):
                    print(colorama.Fore.YELLOW + "⚠ 检测到速率限制错误")
                    await self.download_manager.wait_until_next_hour()
                    # 不标记为失败,下次会重试
                else:
                    await self.download_manager.update_download_status(
                        album_name, track_id, "failed", error_msg, album_id
                    )

        await session.close()

        # 7. 显示最终统计
        final_progress = await self.download_manager.load_progress(album_name)
        print(colorama.Fore.GREEN + self.download_manager.get_download_summary(final_progress))

        # 8. 检查是否全部完成
        if self.download_manager.is_album_complete(final_progress):
            print(colorama.Fore.GREEN + "🎉 专辑下载完成!")
            # 更新全局状态为 completed
            await self.download_manager.update_album_status(
                album_id, album_name, "completed",
                total_count=final_progress["total_count"],
                success_count=final_progress["success_count"]
            )
        else:
            print(colorama.Fore.YELLOW + "⚠ 部分音频下载失败,可重新运行继续下载")
            # 保持 processing 状态
            await self.download_manager.update_album_status(
                album_id, album_name, "processing",
                total_count=final_progress["total_count"],
                success_count=final_progress["success_count"]
            )

    async def _download_single_audio(self, sound_name, sound_url, album_name, session, path, num=None):
        """
        下载单个音频文件

        Returns:
            bool: 下载是否成功
        """
        retries = 3
        logger.debug(f'开始下载声音{sound_name}')

        if num is None:
            sound_name = self.replace_invalid_chars(sound_name)
        else:
            sound_name = f"{num}-{sound_name}"
            sound_name = self.replace_invalid_chars(sound_name)

        if '?' in sound_url:
            file_type = sound_url.split('?')[0][-3:]
        else:
            file_type = sound_url[-3:]

        album_name = self.replace_invalid_chars(album_name)
        download_path = f"{path}/{album_name}"
        os.makedirs(download_path, exist_ok=True)

        file_path = f"{download_path}/{sound_name}.{file_type}"

        # 检查文件是否已存在
        if os.path.exists(file_path):
            print(f'{sound_name}已存在,跳过下载')
            return True

        # 重试下载
        while retries > 0:
            try:
                async with session.get(sound_url, headers=self.default_headers, timeout=120) as response:
                    if response.status == 429:  # Too Many Requests
                        raise Exception("请求过于频繁")

                    async with aiofiles.open(file_path, mode="wb") as f:
                        await f.write(await response.content.read())

                logger.debug(f'{sound_name}下载完成')
                return True

            except Exception as e:
                logger.debug(f'{sound_name}第{4 - retries}次下载失败: {str(e)}')
                logger.debug(traceback.format_exc())
                retries -= 1

                # 检测速率限制错误
                if self.download_manager.is_rate_limited(str(e)):
                    raise  # 向上传播速率限制错误

                if retries > 0:
                    await asyncio.sleep(2)  # 重试前等待2秒

        logger.debug(f'{sound_name}经过三次重试后下载失败')
        return False

    # 解密vip声音url
    def decrypt_url(self, ciphertext):
        key = binascii.unhexlify("aaad3e4fd540b0f79dca95606e72bf93")
        ciphertext = base64.urlsafe_b64decode(ciphertext + '=' * (4 - len(ciphertext) % 4))
        cipher = AES.new(key, AES.MODE_ECB)
        plaintext = cipher.decrypt(ciphertext)
        plaintext = re.sub(r"[^\x20-\x7E]", "", plaintext.decode("utf-8"))
        return plaintext

    # 判断专辑是否为付费专辑，如果是免费专辑返回0，如果是已购买的付费专辑返回1，如果是未购买的付费专辑返回2，如果解析失败返回False
    def judge_album(self, album_id, headers):
        logger.debug(f'开始判断ID为{album_id}的专辑的类型')
        url = "https://www.ximalaya.com/revision/album/v1/simple"
        params = {
            "albumId": album_id
        }
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
        except Exception as e:
            print(colorama.Fore.RED + f'ID为{album_id}的专辑解析失败！')
            logger.debug(f'ID为{album_id}的专辑判断类型失败！')
            logger.debug(traceback.format_exc())
            return False
        logger.debug(f'ID为{album_id}的专辑判断类型成功！')
        if not response.json()["data"]["albumPageMainInfo"]["isPaid"]:
            return 0  # 免费专辑
        elif response.json()["data"]["albumPageMainInfo"]["hasBuy"]:
            return 1  # 已购专辑
        else:
            return 2  # 未购专辑

    # 获取配置文件中的cookie和path
    def analyze_config(self):
        config_path = os.path.join("config_files", "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            os.makedirs("config_files", exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                config = {
                    "cookie": "",
                    "path": ""
                }
                json.dump(config, f)
            return False, False
        try:
            cookie = config["cookie"]
        except Exception:
            config["cookie"] = ""
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f)
            cookie = False
        try:
            path = config["path"]
        except Exception:
            config["path"] = ""
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f)
        return cookie, path

    # 判断cookie是否有效
    def judge_cookie(self, cookie):
        url = "https://www.ximalaya.com/revision/my/getCurrentUserInfo"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1660.14",
            "cookie": cookie
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
        except Exception as e:
            print("无法获取喜马拉雅用户数据，请检查网络状况！")
            logger.debug("无法获取喜马拉雅用户数据！")
            logger.debug(traceback.format_exc())
        if response.json()["ret"] == 200:
            return response.json()["data"]["userName"]
        else:
            return False

    # 登录喜马拉雅账号
    def login(self):
        print("请输入登录方式：")
        print("1. 在浏览器中登录并自动提取cookie")
        print("2. 手动输入cookie")
        choice = input()
        if choice == "1":
            print("请选择浏览器：")
            print("1. Google Chrome")
            print("2. Microsoft Edge")
            choice = input()
            if choice == "1":
                option = webdriver.ChromeOptions()
                option.add_experimental_option("detach", True)
                option.add_experimental_option('excludeSwitches', ['enable-logging'])
                driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
            elif choice == "2":
                option = webdriver.EdgeOptions()
                option.add_experimental_option("detach", True)
                option.add_experimental_option('excludeSwitches', ['enable-logging'])
                driver = webdriver.Edge(EdgeChromiumDriverManager().install(), options=option)
            else:
                return
            print("请在弹出的浏览器中登录喜马拉雅账号，登陆成功浏览器会自动关闭")
            driver.get("https://passport.ximalaya.com/page/web/login")
            try:
                WebDriverWait(driver, 300).until(EC.url_to_be("https://www.ximalaya.com/"))
                cookies = driver.get_cookies()
                logger.debug('以下是使用浏览器登录喜马拉雅账号时的浏览器日志：')
                for entry in driver.get_log('browser'):
                    logger.debug(entry['message'])
                logger.debug('浏览器日志结束')
                driver.quit()
            except selenium.common.exceptions.TimeoutException:
                print("登录超时，自动返回主菜单！")
                logger.debug('以下是使用浏览器登录喜马拉雅账号时的浏览器日志：')
                for entry in driver.get_log('browser'):
                    logger.debug(entry['message'])
                logger.debug('浏览器日志结束')
                driver.quit()
                return
            cookie = ""
            for cookie_ in cookies:
                cookie += f"{cookie_['name']}={cookie_['value']}; "
            config_path = os.path.join("config_files", "config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config["cookie"] = cookie
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f)
        elif choice == "2":
            print("请输入cookie：（获取方法详见README）")
            cookie = input()
            config_path = os.path.join("config_files", "config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config["cookie"] = cookie
            is_cookie_available = self.judge_cookie(cookie)
            if is_cookie_available:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f)
                print("cookie设置成功！")
            else:
                print("cookie无效，将返回主菜单，建议使用方法1自动获取cookie！")
                return
        username = self.judge_cookie(cookie)
        print(f"成功登录账号{username}！")

    async def search_album_by_keyword(self, keyword: str, cookie: str = None) -> tuple:
        """
        根据关键词搜索专辑,返回第一个专辑的ID和名称

        Args:
            keyword: 搜索关键词
            cookie: Cookie字符串(可选,如果没有则自动获取)

        Returns:
            tuple: (album_id, album_name) 或 (None, None)
        """
        from urllib.parse import quote

        logger.info(f"🔍 开始搜索: {keyword}")

        # 如果没有提供cookie,尝试自动获取
        if not cookie:
            try:
                verify_url = f"https://www.ximalaya.com/so/{quote(keyword)}"
                cookies_dict = await slider_solver.solve_slider(verify_url)
                cookie = slider_solver.get_cookies_string(cookies_dict)
                logger.info("✓ 自动获取Cookie成功")
            except Exception as e:
                logger.error(f"❌ 自动获取Cookie失败: {e}")
                return None, None

        # 构造搜索请求
        params = {
            "core": "all",
            "kw": keyword,
            "spellchecker": "true",
            "device": "iPhone",
            "live": "true",
        }

        encoded_kw = quote(keyword)
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Referer": f"https://www.ximalaya.com/so/{encoded_kw}",
            "Cookie": cookie,
            "User-Agent": self.default_headers["user-agent"],
            "xm-sign": sign_generator.get_xm_sign()
        }

        try:
            # 发送搜索请求
            resp = requests.get(self.search_url, headers=headers, params=params, timeout=15)

            if resp.status_code != 200:
                logger.error(f"❌ 搜索请求失败: HTTP {resp.status_code}")
                return None, None

            data = resp.json()

            # 检查是否需要验证
            if data.get("ret") == 200:
                reason = data.get("data", {}).get("reason")
                if reason == "risk invalid":
                    logger.warning("⚠️ 需要滑块验证,尝试重新获取Cookie")
                    # 重新获取cookie并重试一次
                    try:
                        verify_url = f"https://www.ximalaya.com/so/{encoded_kw}"
                        cookies_dict = await slider_solver.solve_slider(verify_url)
                        cookie = slider_solver.get_cookies_string(cookies_dict)
                        headers["Cookie"] = cookie
                        headers["xm-sign"] = sign_generator.get_xm_sign()

                        resp = requests.get(self.search_url, headers=headers, params=params, timeout=15)
                        data = resp.json()
                    except Exception as e:
                        logger.error(f"❌ 重新验证失败: {e}")
                        return None, None

            # 解析搜索结果
            album_data = data.get("data", {}).get("album", {})
            docs = album_data.get("docs", [])

            if not docs:
                logger.warning(f"⚠️ 未找到相关专辑: {keyword}")
                return None, None

            # 获取第一个专辑
            first_album = docs[0]
            album_id = str(first_album.get("albumId", ""))
            album_title = first_album.get("title", "")

            if not album_id:
                logger.error("❌ 专辑ID为空")
                return None, None

            logger.info(f"✓ 搜索成功: {album_title} (ID: {album_id})")
            return album_id, album_title

        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}", exc_info=True)
            return None, None
