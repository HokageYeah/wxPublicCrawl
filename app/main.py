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






from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import sys
import traceback

from app.core.config import settings
from app.api.api import api_router
from app.db.sqlalchemy_db import database
from fastapi.exceptions import RequestValidationError, HTTPException, ResponseValidationError
from app.middleware.exception_handlers import request_validation_error_handler, http_exception_handler, response_validation_error_handler
from app.middleware.response_validator import ResponseValidatorMiddleware
from app.schemas.common_data import ApiResponseData, PlatformEnum
from contextlib import asynccontextmanager
from typing import AsyncIterator
# ✅ 只导入，不调用
from app.core.logging_uru import setup_logging
# 导入AI助手初始化函数
from app.api.endpoints.ai_assistant import init_ai_assistant
# 导入 MCP Server 管理器
from app.ai.mcp.mcp_server.server_manager import start_local_mcp_server, stop_local_mcp_server


# 创建 lifespan 上下文管理器
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    应用生命周期管理器
    
    处理启动和关闭事件，替代已弃用的 @app.on_event
    """
    # 启动事件 - yield 之前的代码在应用启动时执行
    try:
        print("\n" + "=" * 80)
        print("🚀 应用启动中...")
        print("=" * 80)
        
        # 初始化日志系统
        print("📝 初始化日志系统...")
        setup_logging()
        print("✅ 日志系统初始化完成")
        
        # 创建数据库连接
        print("🗄️  初始化数据库连接...")
        database.connect()
        print("✅ 数据库连接完成")

        # 1. 启动本地 MCP Server
        print("🔌 启动本地 MCP Server...")
        try:
            await start_local_mcp_server()
            print("✅ MCP Server 启动完成 - 地址: http://localhost:8008/mcp")
            logging.info("MCP Server 启动完成")
        except Exception as e:
            print(f"⚠️  MCP Server 启动失败: {e}")
            logging.warning(f"MCP Server 启动失败: {e}")
            logging.warning("应用将继续运行，但本地 MCP Server 功能不可用")
        
        # 2. 初始化AI助手
        print("🤖 初始化AI助手...")
        try:
            await init_ai_assistant(llm_conn=None)
            print("✅ AI助手初始化完成")
            logging.info("AI助手初始化完成")
        except Exception as e:
            print(f"⚠️  AI助手初始化失败: {e}")
            logging.warning(f"AI助手初始化失败: {e}")
            logging.warning("应用将继续运行，但AI助手功能不可用")
        
        print("=" * 80)
        print("✅ 应用启动完成")
        print("=" * 80 + "\n")
        
        logging.info("应用启动完成")
        
    except Exception as e:
        print("=" * 80)
        print("❌ 应用启动失败:")
        print(f"错误: {e}")
        print(traceback.format_exc())
        print("=" * 80)
        raise
    
    # 应用运行 - yield 让应用开始接收请求
    yield
    
    # 关闭事件 - yield 之后的代码在应用关闭时执行
    print("\n🛑 应用正在关闭...")
    logging.info("应用正在关闭...")
    
    # 停止本地 MCP Server
    try:
        print("🔌 停止本地 MCP Server...")
        await stop_local_mcp_server()
        print("✅ MCP Server 已停止")
        logging.info("MCP Server 已停止")
    except Exception as e:
        print(f"⚠️  停止 MCP Server 失败: {e}")
        logging.warning(f"停止 MCP Server 失败: {e}")
    
    # 这里可以添加清理逻辑，比如关闭数据库连接
    # if database.is_connected:
    #     database.disconnect()
    #     logging.info("数据库连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan
)

# ============================================================
# 🔥 全局异常捕获中间件 - 用于调试 500 错误
# ============================================================
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """捕获所有未处理的异常并记录详细信息"""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        # 记录完整的错误堆栈
        error_detail = {
            "error": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc(),
            "path": str(request.url),
            "method": request.method
        }
        
        # 打印到控制台
        print("=" * 80)
        print("🔥 捕获到未处理的异常:")
        print(f"路径: {request.method} {request.url}")
        print(f"错误类型: {type(exc).__name__}")
        print(f"错误信息: {str(exc)}")
        print("-" * 80)
        print("完整堆栈:")
        print(traceback.format_exc())
        print("=" * 80)
        
        # 记录到日志
        logging.error(f"未处理的异常: {error_detail}")
        
        # 返回详细的错误信息（开发/调试时）
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
                "error": str(exc),
                "type": type(exc).__name__,
                "path": str(request.url),
                # 生产环境中可以移除 traceback
                "traceback": traceback.format_exc().split('\n')
            }
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
# 定义全局错误处理器，单独封装成一个中间价，并且统一返回相同的格式
app.add_exception_handler(HTTPException, http_exception_handler)
# 定义全局响应格式验证异常处理器
app.add_exception_handler(ResponseValidationError, response_validation_error_handler)

# 添加响应格式验证中间件
app.add_middleware(ResponseValidatorMiddleware)

# 添加路由
app.include_router(api_router, prefix=settings.API_PREFIX)


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
        try:
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
                return JSONResponse(
                    status_code=500,
                    content={"error": "index.html not found", "path": index_path}
                )
        except Exception as e:
            print(f"❌ 服务静态文件时出错: {e}")
            print(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )

else:
    print(f"⚠️  警告: 前端资源目录不存在，API 模式运行")
    
    @app.get("/")
    async def root():
        return {
            "message": "微信公众号爬虫API (前端未构建)",
            "web_dist_path": web_dist_path,
            "exists": os.path.exists(web_dist_path)
        }

# ============================================================
# 健康检查端点 - 用于调试
# ============================================================
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "environment": os.getenv("ENV", "unknown"),
        "python_version": sys.version,
        "is_packaged": hasattr(sys, '_MEIPASS'),
        "base_path": sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.getcwd(),
        "web_dist_path": web_dist_path,
        "web_dist_exists": os.path.exists(web_dist_path)
    }


if __name__ == "__main__":
    import uvicorn
    logging.info("启动应用服务器...")
    uvicorn.run("app.main:app", host="localhost", port=8002, reload=True)