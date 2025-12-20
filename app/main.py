# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# import logging

# from app.core.config import settings
# from app.api.api import api_router
# from app.db.sqlalchemy_db import database
# from fastapi.exceptions import RequestValidationError, HTTPException, ResponseValidationError
# from app.middleware.exception_handlers import request_validation_error_handler, http_exception_handler, response_validation_error_handler
# from app.middleware.response_validator import ResponseValidatorMiddleware
# from app.schemas.common_data import ApiResponseData, PlatformEnum

# # ✅ 只导入，不调用
# from app.core.logging_uru import setup_logging

# # 创建 FastAPI 应用
# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     description=settings.PROJECT_DESCRIPTION,
#     version=settings.PROJECT_VERSION,
#     openapi_url=f"{settings.API_PREFIX}/openapi.json"
# )

# # 设置CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 定义全局异常处理器
# app.add_exception_handler(RequestValidationError, request_validation_error_handler)
# app.add_exception_handler(HTTPException, http_exception_handler)
# app.add_exception_handler(ResponseValidationError, response_validation_error_handler)

# # 添加响应格式验证中间件
# app.add_middleware(ResponseValidatorMiddleware)

# # 添加路由
# app.include_router(api_router, prefix=settings.API_PREFIX)

# # ✅ 使用生命周期事件来初始化
# @app.on_event("startup")
# async def startup_event():
#     """应用启动时执行"""
#     # 初始化日志系统
#     setup_logging()
    
#     # 创建数据库连接
#     print('database.connect() - 启动时初始化')
#     database.connect()
    
#     logging.info("应用启动完成")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """应用关闭时执行"""
#     logging.info("应用正在关闭...")
#     # 这里可以添加清理逻辑，比如关闭数据库连接
#     # database.disconnect()

# # 挂载静态文件 (用于桌面端或前后端同源部署)
# import os
# from fastapi.staticfiles import StaticFiles

# # 获取项目根目录
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# web_dist_path = os.path.join(project_root, "web", "dist")

# if os.path.exists(web_dist_path):
#     # 挂载 /crawl-desktop/assets
#     app.mount("/crawl-desktop/assets", StaticFiles(directory=os.path.join(web_dist_path, "assets")), name="assets")
    
#     from starlette.responses import FileResponse, RedirectResponse

#     # 根路径跳转到 /crawl-desktop/
#     @app.get("/")
#     async def root():
#         return RedirectResponse("/crawl-desktop/")

#     # 处理 /crawl-desktop/ 及其子路径
#     @app.get("/crawl-desktop", include_in_schema=False)
#     @app.get("/crawl-desktop/{full_path:path}", include_in_schema=False)
#     async def serve_spa(full_path: str = ""):
#         # 尝试直接服务 dist 目录下的文件（如 favicon.svg）
#         file_path = os.path.join(web_dist_path, full_path)
#         if full_path and os.path.isfile(file_path):
#              return FileResponse(file_path)
        
#         # 否则返回 index.html
#         return FileResponse(os.path.join(web_dist_path, "index.html"))

# else:
#     # 如果没有构建前端，则返回 API 提示
#     @app.get("/")
#     async def root():
#         return {"message": "微信公众号爬虫API (前端未构建)"}

# if __name__ == "__main__":
#     import uvicorn
#     logging.info("启动应用服务器...")
#     uvicorn.run("app.main:app", host="localhost", port=8002, reload=True)




from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import sys

from app.core.config import settings
from app.api.api import api_router
from app.db.sqlalchemy_db import database
from fastapi.exceptions import RequestValidationError, HTTPException, ResponseValidationError
from app.middleware.exception_handlers import request_validation_error_handler, http_exception_handler, response_validation_error_handler
from app.middleware.response_validator import ResponseValidatorMiddleware
from app.schemas.common_data import ApiResponseData, PlatformEnum

# ✅ 只导入，不调用
from app.core.logging_uru import setup_logging

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义全局异常处理器
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ResponseValidationError, response_validation_error_handler)

# 添加响应格式验证中间件
app.add_middleware(ResponseValidatorMiddleware)

# 添加路由
app.include_router(api_router, prefix=settings.API_PREFIX)

# ✅ 使用生命周期事件来初始化
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 初始化日志系统
    setup_logging()
    
    # 创建数据库连接
    print('database.connect() - 启动时初始化')
    database.connect()
    
    logging.info("应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logging.info("应用正在关闭...")
    # 这里可以添加清理逻辑，比如关闭数据库连接
    # database.disconnect()


# ============================================================
# 静态文件服务 (支持 PyInstaller 打包)
# ============================================================

def get_resource_path(relative_path):
    """获取资源文件的绝对路径(支持打包后)"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        path = os.path.join(sys._MEIPASS, relative_path)
        print(f"📦 打包模式 - 资源路径: {path}")
        return path
    else:
        # 开发环境：从项目根目录计算
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)
        print(f"🔧 开发模式 - 资源路径: {path}")
        return path

# 获取前端资源路径
web_dist_path = get_resource_path("web/dist")

print(f"🌐 前端资源路径: {web_dist_path}")
print(f"🌐 路径是否存在: {os.path.exists(web_dist_path)}")

if os.path.exists(web_dist_path):
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import FileResponse, RedirectResponse
    
    # 检查 assets 目录
    assets_path = os.path.join(web_dist_path, "assets")
    if os.path.exists(assets_path):
        print(f"✅ 挂载静态资源: /crawl-desktop/assets -> {assets_path}")
        app.mount("/crawl-desktop/assets", StaticFiles(directory=assets_path), name="assets")
    else:
        print(f"⚠️  警告: assets 目录不存在: {assets_path}")
    
    # 根路径跳转
    @app.get("/")
    async def root():
        return RedirectResponse("/crawl-desktop/")
    
    # 处理 SPA 路由
    @app.get("/crawl-desktop", include_in_schema=False)
    @app.get("/crawl-desktop/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = ""):
        # 尝试直接服务文件
        if full_path:
            file_path = os.path.join(web_dist_path, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
        
        # 返回 index.html
        index_path = os.path.join(web_dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return {"error": "index.html not found", "path": index_path}

else:
    print(f"⚠️  警告: 前端资源目录不存在，API 模式运行")
    
    @app.get("/")
    async def root():
        return {
            "message": "微信公众号爬虫API (前端未构建)",
            "web_dist_path": web_dist_path,
            "exists": os.path.exists(web_dist_path)
        }


if __name__ == "__main__":
    import uvicorn
    logging.info("启动应用服务器...")
    uvicorn.run("app.main:app", host="localhost", port=8002, reload=True)