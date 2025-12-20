from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.api import api_router
from app.db.sqlalchemy_db import database
from fastapi.exceptions import RequestValidationError, HTTPException, ResponseValidationError
from app.middleware.exception_handlers import request_validation_error_handler, http_exception_handler, response_validation_error_handler
from app.middleware.response_validator import ResponseValidatorMiddleware
from app.schemas.common_data import ApiResponseData, PlatformEnum

# 初始化日志系统（这个是系统日志，操作复杂，设置复杂，所以先舍弃）
# setup_logging()

# 使用loguru初始化日志系统
from app.core.logging_uru import setup_logging
setup_logging()


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


# 定义全局请求参数异常处理器exception_class : 要处理的异常类型、handler : 处理异常的函数
app.add_exception_handler(RequestValidationError, request_validation_error_handler)

# 定义全局错误处理器，单独封装成一个中间价，并且统一返回相同的格式
app.add_exception_handler(HTTPException, http_exception_handler)

# 定义全局响应格式验证异常处理器
app.add_exception_handler(ResponseValidationError, response_validation_error_handler)

# 添加响应格式验证中间件
app.add_middleware(ResponseValidatorMiddleware)


# 添加路由
app.include_router(api_router, prefix=settings.API_PREFIX)

# 创建数据库连接池
print('database.connect()3')
database.connect()

# @app.get("/")
# async def root():
#     return {"message": "微信公众号爬虫API"}

# 挂载静态文件 (用于桌面端或前后端同源部署)
import os
from fastapi.staticfiles import StaticFiles

# 获取项目根目录 (假设 run_app.py 或 run_desktop.py 在根目录)
# 或者使用 app/utils/src_path.py 中的 root_path
# 这里直接计算相对路径，确保指向 web/dist
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
web_dist_path = os.path.join(project_root, "web", "dist")

if os.path.exists(web_dist_path):
    # 挂载 /crawl-desktop/assets
    app.mount("/crawl-desktop/assets", StaticFiles(directory=os.path.join(web_dist_path, "assets")), name="assets")
    
    from starlette.responses import FileResponse, RedirectResponse

    # 根路径跳转到 /crawl-desktop/
    @app.get("/")
    async def root():
        return RedirectResponse("/crawl-desktop/")

    # 处理 /crawl-desktop/ 及其子路径
    @app.get("/crawl-desktop", include_in_schema=False)
    @app.get("/crawl-desktop/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = ""):
        # 尝试直接服务 dist 目录下的文件（如 favicon.svg）
        file_path = os.path.join(web_dist_path, full_path)
        if full_path and os.path.isfile(file_path):
             return FileResponse(file_path)
        
        # 否则返回 index.html
        return FileResponse(os.path.join(web_dist_path, "index.html"))

else:
    # 如果没有构建前端，则返回 API 提示
    @app.get("/")
    async def root():
        return {"message": "微信公众号爬虫API (前端未构建)"}

if __name__ == "__main__":
    import uvicorn
    logging.info("启动应用服务器...")
    uvicorn.run("app.main:app", host="localhost", port=8002, reload=True)
