import platform
import subprocess
import os
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional
from app.utils.src_path import get_writable_dir
from app.models.search_tag import SearchTag
from app.models.user_behavior import UserBehavior, BehaviorType
from app.db.sqlalchemy_db import database
from sqlalchemy.exc import IntegrityError
from loguru import logger
from fastapi import HTTPException

class SystemManager:
    """管理用户会话的单例类"""
    
    _instance = None
    _session_file = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化会话文件路径
            session_dir = get_writable_dir('sessions')
            cls._session_file = os.path.join(session_dir, 'user_session.json')
            
            # 确保初始化默认标签（如果数据库连接可用）
            try:
                # 只有在数据库连接初始化后才能调用，这里可能需要一种机制确保 DB init 之后调用
                # 由于 SystemManager 在 system.py 中初始化，而 database 在 sqlalchemy_db.py 初始化
                # 它们之间可能存在循环依赖如果在这里直接调用。
                # 更好的方式是在应用启动时调用，或者在首次获取标签时调用。
                pass
            except Exception:
                pass
                
        return cls._instance
    

    def fetch_select_folder(self):
        # 换成中文注释
        """
        打开一个本地文件夹选择对话框，并返回选择的文件夹路径。
        支持macOS via AppleScript和Windows via tkinter (fallback).
        """ 
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                # 使用AppleScript 更好的本地体验和避免主线程问题
                script = """
                set p to POSIX path of (choose folder with prompt "Select Download Folder")
                return p
                """
                result = subprocess.run(
                    ['osascript', '-e', script], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    return {"path": result.stdout.strip()}
                else:
                    # 用户可能取消了
                    return {"path": ""}
                    
            else:  # Windows / Linux fallback
                import tkinter as tk
                from tkinter import filedialog
                
                # 注意：在非主线程中使用tkinter可能会出现问题。
                # 理想情况下，应该在单独的进程中运行或通过适当的UI集成运行。
                # 对于简单的本地工具，创建一个隐藏的主窗口可能可以工作。
                root = tk.Tk()
                root.withdraw()  # 隐藏主窗口
                root.attributes('-topmost', True) # 置顶
                folder_path = filedialog.askdirectory()
                root.destroy()
                return {"path": folder_path}
                
        except Exception as e:
            print(f"Error selecting folder: {e}")
            return {"path": "", "error": str(e)}
    
    # def save_session(self, user_info: Dict[str, Any], cookies: Optional[Dict[str, Any]] = None, token: Optional[str] = None) -> bool:
    #     """
    #     保存用户会话 (包括cookies和token)
        
    #     Args:
    #         user_info: 用户信息字典
    #         cookies: 用户cookies字典 (可选)
    #         token: 用户token字符串 (可选)
            
    #     Returns:
    #         bool: 是否保存成功
    #     """
    #     try:
    #         session_data = {
    #             'user_info': user_info,
    #             'cookies': cookies or {},
    #             'token': token or '',
    #             'created_at': datetime.now().isoformat(),
    #             'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
    #         }
            
    #         with open(self._session_file, 'w', encoding='utf-8') as f:
    #             json.dump(session_data, f, ensure_ascii=False, indent=2)
            
    #         print(f"✓ 会话已保存到: {self._session_file}")
    #         return True
            
    #     except Exception as e:
    #         print(f"✗ 保存会话失败: {e}")
    #         return False
    
    # def load_session(self) -> Optional[Dict[str, Any]]:
    #     """
    #     加载用户会话 (包括cookies和token)
        
    #     Returns:
    #         Optional[Dict]: 包含 user_info, cookies 和 token，如果会话不存在或已过期则返回 None
    #     """
    #     try:
    #         if not os.path.exists(self._session_file):
    #             print("会话文件不存在")
    #             return None
            
    #         with open(self._session_file, 'r', encoding='utf-8') as f:
    #             session_data = json.load(f)
            
    #         # 检查会话是否过期
    #         expires_at = datetime.fromisoformat(session_data['expires_at'])
    #         if datetime.now() > expires_at:
    #             print("会话已过期")
    #             self.clear_session()
    #             return None
            
    #         print(f"✓ 会话加载成功")
    #         return {
    #             'user_info': session_data['user_info'],
    #             'cookies': session_data.get('cookies', {}),
    #             'token': session_data.get('token', '')
    #         }
            
    #     except Exception as e:
    #         print(f"✗ 加载会话失败: {e}")
    #         return None
    
    # def clear_session(self) -> bool:
    #     """
    #     清除用户会话
        
    #     Returns:
    #         bool: 是否清除成功
    #     """
    #     try:
    #         if os.path.exists(self._session_file):
    #             os.remove(self._session_file)
    #             print("✓ 会话已清除")
    #         return True
            
    #     except Exception as e:
    #         print(f"✗ 清除会话失败: {e}")
    #         return False
    
    # def is_logged_in(self) -> bool:
    #     """检查用户是否已登录"""
    #     return self.load_session() is not None

    # ------------------------------------------------------------
    # 多平台会话管理扩展方法
    # ------------------------------------------------------------

    def save_platform_session(
        self,
        platform: str,
        user_info: Dict[str, Any],
        cookies: Optional[Dict[str, Any]] = None,
        token: Optional[str] = None,
        expires_days: int = 7
    ) -> bool:
        """
        保存指定平台的用户会话

        Args:
            platform: 平台标识（如 'xmly', 'wx' 等）
            user_info: 用户信息字典
            cookies: 用户cookies字典 (可选)
            token: 用户token字符串 (可选)
            expires_days: 过期天数，默认7天

        Returns:
            bool: 是否保存成功
        """
        try:
            session_dir = get_writable_dir('sessions')
            session_file = os.path.join(session_dir, f'{platform}_session.json')

            session_data = {
                'user_info': user_info,
                'cookies': cookies or {},
                'token': token or '',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=expires_days)).isoformat()
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            print(f"✓ {platform} 会话已保存到: {session_file}")
            return True

        except Exception as e:
            print(f"✗ 保存{platform}会话失败: {e}")
            return False

    def load_platform_session(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        加载指定平台的用户会话

        Args:
            platform: 平台标识（如 'xmly', 'wx' 等）

        Returns:
            Optional[Dict]: 包含 user_info, cookies 和 token，如果会话不存在或已过期则返回 None
        """
        try:
            session_dir = get_writable_dir('sessions')
            session_file = os.path.join(session_dir, f'{platform}_session.json')

            if not os.path.exists(session_file):
                print(f"{platform} 会话文件不存在")
                return None

            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # 检查会话是否过期
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                print(f"{platform} 会话已过期")
                self.clear_platform_session(platform)
                return None

            print(f"✓ {platform} 会话加载成功")
            return {
                'user_info': session_data['user_info'],
                'cookies': session_data.get('cookies', {}),
                'token': session_data.get('token', '')
            }

        except Exception as e:
            print(f"✗ 加载{platform}会话失败: {e}")
            return None

    def clear_platform_session(self, platform: str) -> bool:
        """
        清除指定平台的用户会话

        Args:
            platform: 平台标识（如 'xmly', 'wx' 等）

        Returns:
            bool: 是否清除成功
        """
        try:
            session_dir = get_writable_dir('sessions')
            session_file = os.path.join(session_dir, f'{platform}_session.json')

            if os.path.exists(session_file):
                os.remove(session_file)
                print(f"✓ {platform} 会话已清除")
            return True

        except Exception as e:
            print(f"✗ 清除{platform}会话失败: {e}")
            return False

    def is_platform_logged_in(self, platform: str) -> bool:
        """
        检查指定平台是否已登录

        Args:
            platform: 平台标识（如 'xmly', 'wx' 等）

        Returns:
            bool: 是否已登录
        """
        return self.load_platform_session(platform) is not None

    # ------------------------------------------------------------
    # 标签管理相关方法
    # ------------------------------------------------------------

    def init_default_tags(self):
        """初始化默认标签"""
        default_tags = ["郑州", "教育", "金水区", "中原区", "小学", "惠济区"]
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            # 检查是否已有便签
            count = session.query(SearchTag).count()
            if count == 0:
                print("初始化默认搜索标签...")
                for tag_name in default_tags:
                    tag = SearchTag(name=tag_name)
                    session.add(tag)
                session.commit()
                print("默认标签初始化完成")
        except Exception as e:
            print(f"初始化默认标签失败: {e}")
            session.rollback()
        finally:
            session.close()

    def get_tags(self):
        """获取所有搜索标签"""
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            tags = session.query(SearchTag).all()
            return [{"id": tag.id, "name": tag.name} for tag in tags]
        except Exception as e:
            print(f"获取标签失败: {e}")
            return []
        finally:
            session.close()

    def add_tag(self, name: str):
        """添加新标签"""
        # 限制标签数量最多20个
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            count = session.query(SearchTag).count()
            if count >= 20:
                return {"success": False, "message": "标签数量已达上限(20个)"}
            
            new_tag = SearchTag(name=name)
            session.add(new_tag)
            session.commit()
            return {"success": True, "message": "添加成功", "data": {"id": new_tag.id, "name": new_tag.name}}
        except IntegrityError:
            session.rollback()
            return {"success": False, "message": "标签已存在"}
        except Exception as e:
            session.rollback()
            print(f"添加标签失败: {e}")
            return {"success": False, "message": f"添加失败: {str(e)}"}
        finally:
            session.close()

    def delete_tag(self, tag_id: int):
        """根据ID删除标签"""
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            tag = session.query(SearchTag).filter(SearchTag.id == tag_id).first()
            if tag:
                session.delete(tag)
                session.commit()
                return {"success": True, "message": "删除成功"}
            return {"success": False, "message": "标签不存在"}
        except Exception as e:
            session.rollback()
            print(f"删除标签失败: {e}")
            return {"success": False, "message": f"删除失败: {str(e)}"}
        finally:
            session.close()
            
    def delete_tag_by_name(self, name: str):
        """根据名称删除标签"""
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            # 兼容处理
            tag = session.query(SearchTag).filter(SearchTag.name == name).first()
            if tag:
                session.delete(tag)
                session.commit()
                return {"success": True, "message": "删除成功"}
            return {"success": False, "message": "标签不存在"}
        except Exception as e:
            session.rollback()
            print(f"删除标签失败: {e}")
            return {"success": False, "message": f"删除失败: {str(e)}"}
        finally:
            session.close()

    # ------------------------------------------------------------
    # 用户行为管理相关方法
    # ------------------------------------------------------------

    def set_user_behavior(self, user_id: str, behavior_type: str, behavior_value: str):
        """
        设置用户行为（自动更新或创建）

        Args:
            user_id: 用户ID（uin 或 nick_name）
            behavior_type: 行为类型（使用 BehaviorType 常量）
            behavior_value: 行为值

        Returns:
            dict: 操作结果
        """
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            # 查找是否已存在该用户的行为记录
            behavior = session.query(UserBehavior).filter(
                UserBehavior.user_id == user_id,
                UserBehavior.behavior_type == behavior_type
            ).first()

            if behavior:
                # 更新现有记录
                behavior.behavior_value = behavior_value
                behavior.updated_at = datetime.now()
                print(f"更新用户行为: user_id={user_id}, type={behavior_type}, value={behavior_value}")
            else:
                # 创建新记录
                behavior = UserBehavior(
                    user_id=user_id,
                    behavior_type=behavior_type,
                    behavior_value=behavior_value
                )
                session.add(behavior)
                print(f"新增用户行为: user_id={user_id}, type={behavior_type}, value={behavior_value}")

            session.commit()
            return {"success": True, "message": "保存成功"}
        except Exception as e:
            session.rollback()
            print(f"保存用户行为失败: {e}")
            return {"success": False, "message": f"保存失败: {str(e)}"}
        finally:
            session.close()

    def get_user_behavior(self, user_id: str, behavior_type: str) -> Optional[str]:
        """
        获取用户行为值

        Args:
            user_id: 用户ID（uin 或 nick_name）
            behavior_type: 行为类型（使用 BehaviorType 常量）

        Returns:
            Optional[str]: 行为值，如果不存在则返回 None
        """
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            behavior = session.query(UserBehavior).filter(
                UserBehavior.user_id == user_id,
                UserBehavior.behavior_type == behavior_type
            ).first()

            if behavior:
                print(f"获取用户行为: user_id={user_id}, type={behavior_type}, value={behavior.behavior_value}")
                return behavior.behavior_value
            else:
                print(f"用户行为不存在: user_id={user_id}, type={behavior_type}")
                return None
        except Exception as e:
            print(f"获取用户行为失败: {e}")
            return None
        finally:
            session.close()

    def delete_user_behavior(self, user_id: str, behavior_type: str) -> bool:
        """
        删除用户行为

        Args:
            user_id: 用户ID（uin 或 nick_name）
            behavior_type: 行为类型（使用 BehaviorType 常量）

        Returns:
            bool: 是否删除成功
        """
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            behavior = session.query(UserBehavior).filter(
                UserBehavior.user_id == user_id,
                UserBehavior.behavior_type == behavior_type
            ).first()

            if behavior:
                session.delete(behavior)
                session.commit()
                print(f"删除用户行为: user_id={user_id}, type={behavior_type}")
                return True
            else:
                print(f"用户行为不存在，无需删除: user_id={user_id}, type={behavior_type}")
                return False
        except Exception as e:
            session.rollback()
            print(f"删除用户行为失败: {e}")
            return False
        finally:
            session.close()

    def get_all_user_behaviors(self, user_id: str) -> list:
        """
        获取用户的所有行为记录

        Args:
            user_id: 用户ID（uin 或 nick_name）

        Returns:
            list: 用户行为列表，格式 [{"type": "...", "value": "..."}, ...]
        """
        session_gen = database.get_session()
        session = next(session_gen)
        try:
            behaviors = session.query(UserBehavior).filter(
                UserBehavior.user_id == user_id
            ).all()

            result = [
                {
                    "id": b.id,
                    "type": b.behavior_type,
                    "value": b.behavior_value,
                    "created_at": b.created_at.isoformat() if b.created_at else None,
                    "updated_at": b.updated_at.isoformat() if b.updated_at else None
                }
                for b in behaviors
            ]
            print(f"获取用户所有行为: user_id={user_id}, count={len(result)}")
            return result
        except Exception as e:
            print(f"获取用户所有行为失败: {e}")
            return []
        finally:
            session.close()

    # ------------------------------------------------------------
    # 便捷方法：常用用户行为操作
    # ------------------------------------------------------------

    def set_download_path(self, user_id: str, download_path: str, behavior_type: str = BehaviorType.SAVE_DOWNLOAD_PATH) -> dict:
        """
        设置下载路径（便捷方法）

        Args:
            user_id: 用户ID
            download_path: 下载路径

        Returns:
            dict: 操作结果
        """
        return self.set_user_behavior(user_id, behavior_type, download_path)

    def get_download_path(self, user_id: str, behavior_type: str = BehaviorType.SAVE_DOWNLOAD_PATH) -> Optional[str]:
        """
        获取下载路径（便捷方法）

        Args:
            user_id: 用户ID

        Returns:
            Optional[str]: 下载路径，如果不存在则返回 None
        """
        return self.get_user_behavior(user_id, behavior_type)

    def set_save_to_local(self, user_id: str, save_to_local: str) -> dict:
        """
        设置是否保存到本地（便捷方法）

        Args:
            user_id: 用户ID
            save_to_local: "1" 或 "2"

        Returns:
            dict: 操作结果
        """
        return self.set_user_behavior(user_id, BehaviorType.SAVE_TO_LOCAL, save_to_local)

    def get_save_to_local(self, user_id: str) -> Optional[str]:
        """
        获取是否保存到本地（便捷方法）

        Args:
            user_id: 用户ID

        Returns:
            Optional[str]: "1" 或 "2"，如果不存在则返回 None
        """
        return self.get_user_behavior(user_id, BehaviorType.SAVE_TO_LOCAL)

    def set_upload_to_aliyun(self, user_id: str, upload_to_aliyun: str) -> dict:
        """
        设置是否上传到阿里云（便捷方法）

        Args:
            user_id: 用户ID
            upload_to_aliyun: "1" 或 "2"

        Returns:
            dict: 操作结果
        """
        return self.set_user_behavior(user_id, BehaviorType.UPLOAD_TO_ALIYUN, upload_to_aliyun)

    def get_upload_to_aliyun(self, user_id: str) -> Optional[str]:
        """
        获取是否上传到阿里云（便捷方法）

        Args:
            user_id: 用户ID

        Returns:
            Optional[str]: "1" 或 "2"，如果不存在则返回 None
        """
        return self.get_user_behavior(user_id, BehaviorType.UPLOAD_TO_ALIYUN)

    async  def get_ximalaya_album_download_status(self, user_id: str, album_id: str) -> Optional[Dict]:
        """
        获取喜马拉雅专辑的下载状态

        Args:
            user_id: 用户ID
            album_id: 专辑ID

        Returns:
            Optional[Dict]: 专辑下载状态，如果不存在则返回 None
        """
        try:
            from app.utils.src_path import get_writable_dir
            import aiofiles
            import asyncio

            # 1. 获取下载路径
            download_path = self.get_download_path(user_id, BehaviorType.XIMALAYA_DOWNLOAD_PATH)
            print(f'专辑的下载路径是 {download_path}')
            if not download_path:
                raise HTTPException(status_code=404, detail="专辑下载路径不存在")
                return None

            # 2. 获取全局专辑状态文件路径
            status_file = os.path.join(download_path, "albums_status.json")
            print(f'专辑的下载路径是 status_file {status_file}')
            if not os.path.exists(status_file):
                raise HTTPException(status_code=404, detail="专辑下载状态文件不存在")
                return None

            # 3. 异步读取全局状态
            async with aiofiles.open(status_file, "r", encoding="utf-8") as f:
                content = await f.read()
                global_status = json.loads(content)

            print(f'专辑的下载路径是 global_status {global_status}')
            # 4. 查找专辑信息
            album_key = str(album_id)
            if album_key not in global_status:
                raise HTTPException(status_code=404, detail="专辑下载状态不存在")
                return None

            album_info = global_status[album_key]
            album_name = album_info.get("album_name")
            if not album_name:
                raise HTTPException(status_code=404, detail="专辑名称不存在")
                return None

            # 5. 读取下载进度文件
            from app.utils.download_manager import DownloadManager
            download_manager = DownloadManager(download_path)
            progress = await download_manager.load_progress(album_name)

            if not progress:
                return {
                    "album_id": album_id,
                    "album_name": album_name,
                    "total_count": 0,
                    "success_count": 0,
                    "failed_count": 0,
                    "downloads": {}
                }

            # 6. 构建下载状态信息
            return {
                "album_id": album_id,
                "album_name": album_name,
                "total_count": progress.get("total_count", 0),
                "success_count": progress.get("success_count", 0),
                "failed_count": progress.get("failed_count", 0),
                "downloads": progress.get("downloads", {})
            }

        except Exception as e:
            logger.error(f"获取专辑下载状态失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取专辑下载状态失败: {str(e)}")


# 全局单例
system_manager = SystemManager()