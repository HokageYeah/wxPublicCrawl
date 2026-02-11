import logging
import sys
import os
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel
from loguru import logger

from app.core.config import settings


class LoggingSettings(BaseModel):
    LOGGING_LEVEL: str = "INFO"
    LOGGERS: List[str] = [""]


logging_settings = LoggingSettings()

# ✅ 添加初始化标志，防止重复初始化
_logging_initialized = False


def setup_logging() -> None:
    """设置日志配置"""
    global _logging_initialized
    
    # ✅ 如果已经初始化过，直接返回
    if _logging_initialized:
        return
    
    # 移除默认的处理器
    logger.remove()
    
    # 设置日志级别
    log_level = logging_settings.LOGGING_LEVEL if not settings.DEBUG else "DEBUG"
    
    # 创建日志目录，普通运行日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "app_run")
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名（按日期区分）
    log_filename = os.path.join(log_dir, f"app_run_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # 添加控制台处理器，使用彩色输出, 去除error级别日志
    logger.add(
        sink=sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
        enqueue=True,
        diagnose=True,
    )
    
    # 添加文件日志处理器 主日志（排除 ERROR 及以上）
    logger.add(
        sink=log_filename,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        filter=lambda record: record["level"].no < 40,
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
        diagnose=True,
    )
    
    # 创建错误日志目录
    error_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "app_error")
    os.makedirs(error_log_dir, exist_ok=True)

    # 添加错误日志文件处理器
    error_log_filename = os.path.join(error_log_dir, f"app_error_{datetime.now().strftime('%Y-%m-%d')}.log")
    logger.add(
        sink=error_log_filename,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
        diagnose=True,
    )
    
    # 设置第三方库的日志级别
    for module in ["uvicorn", "uvicorn.access", "uvicorn.error", "httpx", "httpcore"]:
        logger.level(module, logging.WARNING)
    
    # 拦截标准库的日志
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            # 过滤掉 SSE 心跳包的 DEBUG 日志
            # 例如：2025-12-31 12:06:22 | DEBUG    | app.ai.llm.mcp_llm_connect:async_init:129 -    • N/A: N/A
            message = record.getMessage()
            if "ping: b': ping -" in message and record.levelno <= logging.DEBUG:
                return

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, message
            )
    
    # 配置标准库日志处理器
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 替换所有已存在的日志处理器
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    
    # ✅ 标记为已初始化
    _logging_initialized = True
    
    # 日志初始化完成信息
    logger.info("日志系统初始化完成 - 使用 loguru")


def get_logger(name=None):
    """获取命名的日志记录器"""
    return logger.bind(name=name)