import platform
import subprocess


def fetch_select_folder():
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
