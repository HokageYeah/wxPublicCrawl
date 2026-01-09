"""
LLM配置数据模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ModelTypeEnum(str, Enum):
    """模型类型枚举"""
    GPT = "GPT"
    CLAUDE = "Claude"
    QWEN = "Qwen"
    GLM = "GLM"
    DEEPSEEK = "DeepSeek"
    GEMINI = "Gemini"
    CUSTOM = "Custom"


class ActionEnum(str, Enum):
    """操作类型枚举"""
    CREATE = "create"
    LIST = "list"
    GET = "get"
    UPDATE = "update"
    DELETE = "delete"
    GET_ACTIVE = "get_active"
    SWITCH = "switch"
    GET_MODEL_TYPES = "get_model_types"
    GET_CLIENT_CONFIG = "get_client_config"


# 创建/更新请求模型
class LLMConfigurationCreate(BaseModel):
    """创建LLM配置请求"""
    user_id: Optional[str] = Field(None, description="用户ID，为空表示全局配置")
    model_type: str = Field(..., description="模型类型")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    ai_api_key: str = Field(..., min_length=1, max_length=500, description="AI API密钥")
    ai_base_url: str = Field(..., min_length=1, max_length=500, description="AI API基础URL")
    api_endpoint: Optional[str] = Field(None, max_length=500, description="API端点（如果需要）")
    temperature: Optional[int] = Field(None, ge=0, le=200, description="温度参数（乘以100）")
    max_tokens: Optional[int] = Field(None, gt=0, description="最大Token数")
    top_p: Optional[int] = Field(None, ge=0, le=100, description="Top-P采样参数（乘以100）")
    enable_history: bool = Field(default=False, description="是否启用对话历史")
    max_history: int = Field(default=10, gt=0, description="最大历史记录数")
    enable_stream: bool = Field(default=False, description="是否启用流式响应")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    custom_parameters: Optional[str] = Field(None, description="自定义参数（JSON格式）")
    description: Optional[str] = Field(None, max_length=500, description="配置描述或备注")
    is_active: bool = Field(default=False, description="是否激活")

    @field_validator('model_type')
    @classmethod
    def validate_model_type(cls, v: str) -> str:
        """验证模型类型"""
        valid_types = [item.value for item in ModelTypeEnum]
        if v not in valid_types:
            raise ValueError(f"模型类型必须是: {', '.join(valid_types)}")
        return v


class LLMConfigurationUpdate(BaseModel):
    """更新LLM配置请求"""
    model_type: Optional[str] = Field(None, description="模型类型")
    model_name: Optional[str] = Field(None, min_length=1, max_length=100, description="模型名称")
    ai_api_key: Optional[str] = Field(None, min_length=1, max_length=500, description="AI API密钥")
    ai_base_url: Optional[str] = Field(None, min_length=1, max_length=500, description="AI API基础URL")
    api_endpoint: Optional[str] = Field(None, max_length=500, description="API端点")
    temperature: Optional[int] = Field(None, ge=0, le=200, description="温度参数")
    max_tokens: Optional[int] = Field(None, gt=0, description="最大Token数")
    top_p: Optional[int] = Field(None, ge=0, le=100, description="Top-P采样参数")
    enable_history: Optional[bool] = Field(None, description="是否启用对话历史")
    max_history: Optional[int] = Field(None, gt=0, description="最大历史记录数")
    enable_stream: Optional[bool] = Field(None, description="是否启用流式响应")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    custom_parameters: Optional[str] = Field(None, description="自定义参数")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")
    is_active: Optional[bool] = Field(None, description="是否激活")

    @field_validator('model_type')
    @classmethod
    def validate_model_type(cls, v: Optional[str]) -> Optional[str]:
        """验证模型类型"""
        if v is not None:
            valid_types = [item.value for item in ModelTypeEnum]
            if v not in valid_types:
                raise ValueError(f"模型类型必须是: {', '.join(valid_types)}")
        return v


# 列表查询请求
class LLMConfigurationListRequest(BaseModel):
    """获取LLM配置列表请求"""
    user_id: Optional[str] = Field(None, description="用户ID")
    model_type: Optional[str] = Field(None, description="模型类型过滤")
    is_active: Optional[bool] = Field(None, description="激活状态过滤")
    skip: int = Field(default=0, ge=0, description="跳过数量")
    limit: int = Field(default=100, ge=1, le=100, description="返回数量限制")


# 获取单个配置请求
class LLMConfigurationGetRequest(BaseModel):
    """获取单个LLM配置请求"""
    config_id: int = Field(..., gt=0, description="配置ID")
    user_id: Optional[str] = Field(None, description="用户ID（可选，用于权限控制）")


# 更新配置请求（包含ID）
class LLMConfigurationUpdateWithIdRequest(BaseModel):
    """更新LLM配置请求（包含ID）"""
    config_id: int = Field(..., gt=0, description="配置ID")
    user_id: Optional[str] = Field(None, description="用户ID（可选，用于权限控制）")
    model_type: Optional[str] = Field(None, description="模型类型")
    model_name: Optional[str] = Field(None, min_length=1, max_length=100, description="模型名称")
    ai_api_key: Optional[str] = Field(None, min_length=1, max_length=500, description="AI API密钥")
    ai_base_url: Optional[str] = Field(None, min_length=1, max_length=500, description="AI API基础URL")
    api_endpoint: Optional[str] = Field(None, max_length=500, description="API端点")
    temperature: Optional[int] = Field(None, ge=0, le=200, description="温度参数")
    max_tokens: Optional[int] = Field(None, gt=0, description="最大Token数")
    top_p: Optional[int] = Field(None, ge=0, le=100, description="Top-P采样参数")
    enable_history: Optional[bool] = Field(None, description="是否启用对话历史")
    max_history: Optional[int] = Field(None, gt=0, description="最大历史记录数")
    enable_stream: Optional[bool] = Field(None, description="是否启用流式响应")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    custom_parameters: Optional[str] = Field(None, description="自定义参数")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")
    is_active: Optional[bool] = Field(None, description="是否激活")

    @field_validator('model_type')
    @classmethod
    def validate_model_type(cls, v: Optional[str]) -> Optional[str]:
        """验证模型类型"""
        if v is not None:
            valid_types = [item.value for item in ModelTypeEnum]
            if v not in valid_types:
                raise ValueError(f"模型类型必须是: {', '.join(valid_types)}")
        return v


# 删除配置请求
class LLMConfigurationDeleteRequest(BaseModel):
    """删除LLM配置请求"""
    config_id: int = Field(..., gt=0, description="配置ID")
    user_id: Optional[str] = Field(None, description="用户ID（可选，用于权限控制）")


# 切换配置请求
class LLMConfigSwitchRequest(BaseModel):
    """切换配置请求"""
    config_id: int = Field(..., gt=0, description="配置ID")
    user_id: Optional[str] = Field(None, description="用户ID（可选）")


# 获取激活配置请求
class LLMConfigActiveRequest(BaseModel):
    """获取激活配置请求"""
    user_id: Optional[str] = Field(None, description="用户ID（可选）")


# 获取客户端配置请求
class LLMConfigClientRequest(BaseModel):
    """获取客户端配置请求"""
    user_id: Optional[str] = Field(None, description="用户ID（可选）")


# 响应模型
class LLMConfigurationResponse(BaseModel):
    """LLM配置响应"""
    id: int
    user_id: Optional[str]
    is_active: bool
    model_type: str
    model_name: str
    ai_api_key: str  # 注意：实际应用中可能需要脱敏
    ai_base_url: str
    api_endpoint: Optional[str]
    temperature: Optional[int]
    max_tokens: Optional[int]
    top_p: Optional[int]
    enable_history: bool
    max_history: int
    enable_stream: bool
    system_prompt: Optional[str]
    custom_parameters: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LLMConfigurationMaskedResponse(BaseModel):
    """LLM配置响应（脱敏版）"""
    id: int
    user_id: Optional[str]
    is_active: bool
    model_type: str
    model_name: str
    ai_api_key: str  # 脱敏
    ai_base_url: str
    api_endpoint: Optional[str]
    temperature: Optional[int]
    max_tokens: Optional[int]
    top_p: Optional[int]
    enable_history: bool
    max_history: int
    enable_stream: bool
    system_prompt: Optional[str]
    custom_parameters: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 特殊响应模型
class LLMConfigurationListResponse(BaseModel):
    """LLM配置列表响应"""
    total: int
    items: list[LLMConfigurationMaskedResponse]


class LLMConfigActiveResponse(BaseModel):
    """当前激活的配置响应"""
    id: int
    user_id: Optional[str]
    model_type: str
    model_name: str
    ai_api_key: str  # 脱敏
    ai_base_url: str
    api_endpoint: Optional[str]
    temperature: Optional[int]
    max_tokens: Optional[int]
    top_p: Optional[int]
    enable_history: bool
    max_history: int
    enable_stream: bool
    system_prompt: Optional[str]
    custom_parameters: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True

