import platform
import subprocess
import os
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional
from app.utils.src_path import get_writable_dir

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


# 全局单例
system_manager = SystemManager()