"""
AI 大模型配置数据模型
用于存储和管理不同 AI 模型的配置信息
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.db.sqlalchemy_db import Base
from datetime import datetime


class LLMConfiguration(Base):
    """AI 大模型配置表"""
    __tablename__ = "llm_configuration"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(String(100), nullable=True, index=True, comment="用户ID（uin 或 nick_name），为空表示全局配置")
    
    # 基础配置
    is_active = Column(Boolean, default=False, index=True, comment="是否激活（当前正在使用的配置）")
    model_type = Column(String(50), nullable=False, index=True, comment="模型类型（Qwen, GLM, DeepSeek, GPT, Claude等）")
    model_name = Column(String(100), nullable=False, comment="模型名称（如：gpt-4-turbo）")
    
    # API 配置
    ai_api_key = Column(String(500), nullable=False, comment="AI API 密钥")
    ai_base_url = Column(String(500), nullable=False, comment="AI API 基础 URL")
    api_endpoint = Column(String(500), nullable=True, comment="API 端点（如果需要）")
    
    # 模型参数
    temperature = Column(Integer, nullable=True, comment="温度参数（乘以100）")
    max_tokens = Column(Integer, nullable=True, comment="最大 Token 数")
    top_p = Column(Integer, nullable=True, comment="Top-P 采样参数（乘以100）")
    
    # 功能开关
    enable_history = Column(Boolean, default=False, comment="是否启用对话历史")
    max_history = Column(Integer, default=10, comment="最大历史记录数")
    enable_stream = Column(Boolean, default=False, comment="是否启用流式响应")
    
    # 高级配置
    system_prompt = Column(Text, nullable=True, comment="系统提示词")
    custom_parameters = Column(Text, nullable=True, comment="自定义参数（JSON格式）")
    
    # 备注
    description = Column(String(500), nullable=True, comment="配置描述或备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def __repr__(self):
        active_status = "✅ 激活" if self.is_active else "⚪ 未激活"
        return f"<LLMConfiguration(id={self.id}, model={self.model_name}, status={active_status})>"


# 模型类型枚举
class ModelType:
    """模型类型常量"""
    # OpenAI 系列
    GPT = "GPT"
    
    # Claude 系列
    CLAUDE = "Claude"
    
    # 国产大模型
    QWEN = "Qwen"
    GLM = "GLM"
    DEEPSEEK = "DeepSeek"
    
    # Google
    GEMINI = "Gemini"
    
    # 其他
    CUSTOM = "Custom"  # 自定义模型

