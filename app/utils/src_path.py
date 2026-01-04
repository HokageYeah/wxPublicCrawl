import os
import platform
import sys

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


# 以下都是桌面 程序路径适配
def get_writable_dir(subdir='temp'):
    """
    获取可写目录路径（用于写入文件）
    
    Args:
        subdir: 子目录名称，如 'temp', 'cache', 'qrcodes' 等
    
    Returns:
        str: 可写目录的绝对路径
    """
    if platform.system() == 'Darwin':  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support/wx公众号工具')
    elif platform.system() == 'Windows':
        base_dir = os.path.expanduser('~/AppData/Local/wx公众号工具')
    else:  # Linux
        base_dir = os.path.expanduser('~/.local/share/wx公众号工具')
    
    target_dir = os.path.join(base_dir, subdir)
    # 如果目录不存在，则创建目录 exist_ok=True 表示如果目录存在，则不创建
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def get_temp_file_path(filename):
    """
    获取临时文件的完整路径
    
    Args:
        filename: 文件名, 如 'qrcode.png'
    
    Returns:
        str: 临时文件的完整路径
    """
    temp_dir = get_writable_dir('temp')
    return os.path.join(temp_dir, filename)

def get_npx_bridge_file_path(filename):
    """
    获取npx桥接文件的完整路径
    """
    temp_dir = get_writable_dir('npx_bridge')
    return os.path.join(temp_dir, filename)


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径（用于读取打包后的资源文件）
    
    Args:
        relative_path: 相对于项目根目录的路径，如 'app/ai/prompt/education_prompt.txt'
    
    Returns:
        str: 资源文件的绝对路径
    
    Example:
        # 开发环境: /path/to/project/app/ai/prompt/education_prompt.txt
        # 打包后: /private/var/.../app/ai/prompt/education_prompt.txt
        path = get_resource_path('app/ai/prompt/education_prompt.txt')
    """
    # 优先使用 sys._MEIPASS (PyInstaller 打包后的临时目录)
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        base_path = sys._MEIPASS
        mode = "打包模式"
        if ENV in ("desktop", "production"):
            print(f"📦 [打包模式] sys._MEIPASS: {base_path}")
    else:
        # 开发环境：从当前文件向上找到项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        mode = "开发模式"
        if ENV in ("development", "dev", "test"):
            print(f"🔧 [开发模式] 项目根目录: {base_path}")
    
    full_path = os.path.join(base_path, relative_path)
    
    # 详细日志（调试时启用）
    if ENV in ("development", "dev", "test", "desktop"):
        file_exists = os.path.exists(full_path)
        print(f"📄 [{mode}] 资源路径解析:")
        print(f"   相对路径: {relative_path}")
        print(f"   完整路径: {full_path}")
        print(f"   文件存在: {'✅ 是' if file_exists else '❌ 否'}")
        
        # 如果文件不存在，尝试列出父目录内容帮助调试
        if not file_exists:
            parent_dir = os.path.dirname(full_path)
            if os.path.exists(parent_dir):
                try:
                    contents = os.listdir(parent_dir)
                    print(f"   父目录内容: {contents[:5]}{'...' if len(contents) > 5 else ''}")
                except Exception as e:
                    print(f"   无法列出父目录: {e}")
    
    return full_path


def get_cache_file_path(filename):
    """
    获取缓存文件的完整路径（用于写入）
    
    Args:
        filename: 文件名
    
    Returns:
        str: 文件的完整路径
    """
    cache_dir = get_writable_dir('cache')
    return os.path.join(cache_dir, filename)


def cleanup_old_temp_files(max_age_hours=24):
    """
    清理旧的临时文件
    
    Args:
        max_age_hours: 文件最大保留时间（小时）
    """
    import time
    
    temp_dir = get_writable_dir('temp')
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        
        # 跳过目录
        if os.path.isdir(file_path):
            continue
        
        # 检查文件年龄
        file_age = current_time - os.path.getmtime(file_path)
        
        if file_age > max_age_seconds:
            try:
                os.remove(file_path)
                print(f"清理旧临时文件: {filename}")
            except Exception as e:
                print(f"清理文件失败 {filename}: {e}")


# 使用示例
if __name__ == '__main__':
    print("=" * 60)
    print("文件路径工具测试")
    print("=" * 60)
    
    # 测试资源文件读取（打包后的文件）
    print("\n1. 测试资源文件路径:")
    prompt_path = get_resource_path('app/ai/prompt/education_prompt.txt')
    print(f"   提示词文件路径: {prompt_path}")
    
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read(100)  # 读取前100个字符
            print(f"   文件内容预览: {content}...")
    else:
        print(f"   ❌ 文件不存在！")
    
    # 测试可写文件路径
    print("\n2. 测试可写文件路径:")
    qrcode_path = get_temp_file_path('qrcode.png')
    print(f"   二维码保存路径: {qrcode_path}")
    
    # 清理旧文件
    print("\n3. 清理旧临时文件:")
    cleanup_old_temp_files(max_age_hours=1)