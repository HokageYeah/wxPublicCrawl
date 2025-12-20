import os

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

