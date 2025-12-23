import os
import platform

# 获取工程目录
obj_path = os.path.dirname(os.path.abspath(__file__))

# 获取工程根目录
root_path = os.path.dirname(os.path.dirname(obj_path))

# 获取工程app文件夹目录
app_path = os.path.join(root_path, "app")

# 只在开发环境打印路径信息
ENV = os.getenv("ENV", "development")
if ENV in ("development", "dev", "test"):
    print('obj_path', obj_path)
    print('root_path', root_path)
    print('app_path', app_path)


def get_writable_dir(subdir='temp'):
    """获取可写目录路径"""
    if platform.system() == 'Darwin':  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support/wx公众号工具')
    elif platform.system() == 'Windows':
        base_dir = os.path.expanduser('~/AppData/Local/wx公众号工具')
    else:  # Linux
        base_dir = os.path.expanduser('~/.local/share/wx公众号工具')
    
    target_dir = os.path.join(base_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def get_temp_file_path(filename):
    """获取临时文件的完整路径"""
    temp_dir = get_writable_dir('temp')
    return os.path.join(temp_dir, filename)