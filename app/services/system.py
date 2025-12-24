import platform
import subprocess
import os
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional
from app.utils.src_path import get_writable_dir
from app.models.search_tag import SearchTag
from app.db.sqlalchemy_db import database
from sqlalchemy.exc import IntegrityError

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
    
    def save_session(self, user_info: Dict[str, Any], cookies: Optional[Dict[str, Any]] = None, token: Optional[str] = None) -> bool:
        """
        保存用户会话 (包括cookies和token)
        
        Args:
            user_info: 用户信息字典
            cookies: 用户cookies字典 (可选)
            token: 用户token字符串 (可选)
            
        Returns:
            bool: 是否保存成功
        """
        try:
            session_data = {
                'user_info': user_info,
                'cookies': cookies or {},
                'token': token or '',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            with open(self._session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 会话已保存到: {self._session_file}")
            return True
            
        except Exception as e:
            print(f"✗ 保存会话失败: {e}")
            return False
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        加载用户会话 (包括cookies和token)
        
        Returns:
            Optional[Dict]: 包含 user_info, cookies 和 token，如果会话不存在或已过期则返回 None
        """
        try:
            if not os.path.exists(self._session_file):
                print("会话文件不存在")
                return None
            
            with open(self._session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # 检查会话是否过期
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                print("会话已过期")
                self.clear_session()
                return None
            
            print(f"✓ 会话加载成功")
            return {
                'user_info': session_data['user_info'],
                'cookies': session_data.get('cookies', {}),
                'token': session_data.get('token', '')
            }
            
        except Exception as e:
            print(f"✗ 加载会话失败: {e}")
            return None
    
    def clear_session(self) -> bool:
        """
        清除用户会话
        
        Returns:
            bool: 是否清除成功
        """
        try:
            if os.path.exists(self._session_file):
                os.remove(self._session_file)
                print("✓ 会话已清除")
            return True
            
        except Exception as e:
            print(f"✗ 清除会话失败: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """检查用户是否已登录"""
        return self.load_session() is not None

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


# 全局单例
system_manager = SystemManager()