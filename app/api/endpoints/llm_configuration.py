"""
LLM配置API接口
提供LLM配置的增删改查功能
统一使用POST请求，由中间件统一处理返回格式
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Optional, Dict, Any
from loguru import logger
from app.db.sqlalchemy_db import get_sqlalchemy_db
from app.models.llm_configuration import LLMConfiguration
from app.schemas.llm_configuration import (
    LLMConfigurationCreate,
    LLMConfigurationListRequest,
    LLMConfigurationGetRequest,
    LLMConfigurationUpdateWithIdRequest,
    LLMConfigurationDeleteRequest,
    LLMConfigSwitchRequest,
    LLMConfigActiveRequest,
    LLMConfigClientRequest,
    ModelTypeEnum
)
from app.services.llm_configuration import (
    create_llm_configuration,
    get_llm_configuration_by_id,
    get_llm_configurations,
    update_llm_configuration,
    delete_llm_configuration,
    get_active_llm_configuration,
    switch_active_llm_configuration,
    get_llm_config_for_client,
    mask_api_key
)
from app.schemas.common_data import ApiResponseData


TAG = "LLM_CONFIGURATION_API"

router = APIRouter()


def _ensure_table_exists(db: Session) -> None:
    """
    确保LLM配置表存在，如果不存在则创建
    """
    try:
        # 检查表是否存在
        inspector = inspect(db.bind)
        table_exists = inspector.has_table(LLMConfiguration.__tablename__)
        
        if not table_exists:
            logger.bind(tag=TAG).warning(f"表 {LLMConfiguration.__tablename__} 不存在，正在创建...")
            # 创建表结构
            LLMConfiguration.__table__.create(db.bind, checkfirst=True)
            logger.bind(tag=TAG).success(f"表 {LLMConfiguration.__tablename__} 创建成功")
    except Exception as e:
        logger.bind(tag=TAG).error(f"创建表失败: {e}")
        raise


def _to_masked_response(config: LLMConfiguration) -> Dict[str, Any]:
    """转换为脱敏响应（字典格式）"""
    config_dict = {
        'id': config.id,
        'user_id': config.user_id,
        'is_active': config.is_active,
        'model_type': config.model_type,
        'model_name': config.model_name,
        'ai_api_key': mask_api_key(config.ai_api_key),
        'ai_base_url': config.ai_base_url,
        'api_endpoint': config.api_endpoint,
        'temperature': config.temperature,
        'max_tokens': config.max_tokens,
        'top_p': config.top_p,
        'enable_history': config.enable_history,
        'max_history': config.max_history,
        'enable_stream': config.enable_stream,
        'system_prompt': config.system_prompt,
        'custom_parameters': config.custom_parameters,
        'description': config.description,
        'created_at': config.created_at.isoformat() if config.created_at else None,
        'updated_at': config.updated_at.isoformat() if config.updated_at else None,
    }
    return config_dict


def _to_full_response(config: LLMConfiguration) -> Dict[str, Any]:
    """转换为完整响应（字典格式）"""
    config_dict = {
        'id': config.id,
        'user_id': config.user_id,
        'is_active': config.is_active,
        'model_type': config.model_type,
        'model_name': config.model_name,
        'ai_api_key': config.ai_api_key,
        'ai_base_url': config.ai_base_url,
        'api_endpoint': config.api_endpoint,
        'temperature': config.temperature,
        'max_tokens': config.max_tokens,
        'top_p': config.top_p,
        'enable_history': config.enable_history,
        'max_history': config.max_history,
        'enable_stream': config.enable_stream,
        'system_prompt': config.system_prompt,
        'custom_parameters': config.custom_parameters,
        'description': config.description,
        'created_at': config.created_at.isoformat() if config.created_at else None,
        'updated_at': config.updated_at.isoformat() if config.updated_at else None,
    }
    return config_dict


def _to_active_response(config: LLMConfiguration) -> Dict[str, Any]:
    """转换为激活配置响应（字典格式）"""
    config_dict = {
        'id': config.id,
        'user_id': config.user_id,
        'is_active': config.is_active,
        'model_type': config.model_type,
        'model_name': config.model_name,
        'ai_api_key': mask_api_key(config.ai_api_key),
        'ai_base_url': config.ai_base_url,
        'api_endpoint': config.api_endpoint,
        'temperature': config.temperature,
        'max_tokens': config.max_tokens,
        'top_p': config.top_p,
        'enable_history': config.enable_history,
        'max_history': config.max_history,
        'enable_stream': config.enable_stream,
        'system_prompt': config.system_prompt,
        'custom_parameters': config.custom_parameters,
        'description': config.description,
    }
    return config_dict


@router.post("/llm-config-create", response_model=ApiResponseData)
async def create_config(
    params: LLMConfigurationCreate,
    db: Session = Depends(get_sqlalchemy_db)
):
    """
    创建新的LLM配置
    
    - 如果is_active为True，会自动取消其他配置的激活状态
    - user_id为空时表示全局配置
    
    请求体示例:
    ```json
    {
        "user_id": null,
        "model_type": "GPT",
        "model_name": "gpt-4-turbo",
        "ai_api_key": "your-api-key",
        "ai_base_url": "https://api.openai.com/v1",
        "temperature": 70,
        "max_tokens": 2000,
        "enable_history": true,
        "max_history": 10,
        "description": "GPT-4 Turbo 配置",
        "is_active": true
    }
    ```
    """
    try:
        # 确保表存在
        _ensure_table_exists(db)
        
        logger.bind(tag=TAG).info(f"请求创建LLM配置 - 模型: {params.model_name}")
        
        db_config = create_llm_configuration(db, params)
        
        print("llm-config-create---创建新的LLM配置：", _to_full_response(db_config))

        return _to_full_response(db_config)
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"创建LLM配置失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/llm-config-list", response_model=ApiResponseData)
async def list_configs(
    params: LLMConfigurationListRequest,
    db: Session = Depends(get_sqlalchemy_db)
):
    """
    获取LLM配置列表
    
    - 如果提供user_id，返回该用户的配置 + 全局配置
    - 不提供user_id时，返回所有配置
    
    请求体示例:
    ```json
    {
        "user_id": null,
        "model_type": "GPT",
        "is_active": true,
        "skip": 0,
        "limit": 10
    }
    ```
    """
    try:
        # 确保表存在
        _ensure_table_exists(db)
        
        logger.bind(tag=TAG).info(
            f"请求获取LLM配置列表 - user_id: {params.user_id}, "
            f"model_type: {params.model_type}, is_active: {params.is_active}"
        )
        
        configs, total = get_llm_configurations(
            db=db,
            user_id=params.user_id,
            model_type=params.model_type,
            is_active=params.is_active,
            skip=params.skip,
            limit=params.limit
        )
        
        return {
            "total": total,
            "items": [_to_masked_response(config) for config in configs]
        }
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取LLM配置列表失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/llm-config-get", response_model=ApiResponseData)
async def get_config(
    params: LLMConfigurationGetRequest,
    db: Session = Depends(get_sqlalchemy_db)
):
    """
    获取指定ID的LLM配置（完整信息）
    
    请求体示例:
    ```json
    {
        "config_id": 1,
        "user_id": null
    }
    ```
    """
    try:
        logger.bind(tag=TAG).info(f"请求获取LLM配置 - ID: {params.config_id}")
        
        db_config = get_llm_configuration_by_id(db, params.config_id, params.user_id)
        
        if not db_config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        return _to_full_response(db_config)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取LLM配置失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/llm-config-update", response_model=ApiResponseData)
async def update_config(
    params: LLMConfigurationUpdateWithIdRequest,
    db: Session = Depends(get_sqlalchemy_db)
):
    """
    更新LLM配置
    
    - 如果将is_active改为True，会自动取消其他配置的激活状态
    
    请求体示例:
    ```json
    {
        "config_id": 1,
        "user_id": null,
        "temperature": 80,
        "max_tokens": 4000
    }
    ```
    """
    try:
        logger.bind(tag=TAG).info(f"请求更新LLM配置 - ID: {params.config_id}")
        
        # 提取更新数据（排除config_id和user_id）
        update_data = params.model_dump(exclude={'config_id', 'user_id'}, exclude_unset=True)
        if not update_data:
            update_data = {}
        
        from app.schemas.llm_configuration import LLMConfigurationUpdate
        db_config = update_llm_configuration(
            db,
            params.config_id,
            LLMConfigurationUpdate(**update_data),
            params.user_id
        )
        
        if not db_config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        return _to_full_response(db_config)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.bind(tag=TAG).error(f"更新LLM配置失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/llm-config-delete", response_model=ApiResponseData)
async def delete_config(
    params: LLMConfigurationDeleteRequest,
    db: Session = Depends(get_sqlalchemy_db)
):
    """
    删除LLM配置
    
    请求体示例:
    ```json
    {
        "config_id": 1,
        "user_id": null
    }
    ```
    """
    try:
        logger.bind(tag=TAG).info(f"请求删除LLM配置 - ID: {params.config_id}")
        
        success = delete_llm_configuration(db, params.config_id, params.user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        return {"success": True, "message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.bind(tag=TAG).error(f"删除LLM配置失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/llm-config-active", response_model=ApiResponseData)
async def get_active_config(
    params: LLMConfigActiveRequest,
    db: Session = Depends(get_sqlalchemy_db)
):
    """
    获取当前激活的LLM配置
    
    优先级：
    1. 用户的激活配置
    2. 全局的激活配置
    
    请求体示例:
    ```json
    {
        "user_id": null
    }
    ```
    """
    try:
        # 确保表存在
        _ensure_table_exists(db)
        
        logger.bind(tag=TAG).info(f"请求获取激活配置 - user_id: {params.user_id}")
        
        db_config = get_active_llm_configuration(db, params.user_id)
        
        if not db_config:
            raise HTTPException(status_code=404, detail="未找到激活的配置")
        
        return _to_active_response(db_config)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取激活配置失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/llm-config-switch", response_model=ApiResponseData)
async def switch_config(
    params: LLMConfigSwitchRequest,
    db: Session = Depends(get_sqlalchemy_db)
):
    """
    切换激活的LLM配置
    
    - 取消当前激活的配置
    - 激活指定的配置
    
    请求体示例:
    ```json
    {
        "config_id": 2,
        "user_id": null
    }
    ```
    """
    try:
        logger.bind(tag=TAG).info(f"请求切换激活配置 - config_id: {params.config_id}")
        
        db_config = switch_active_llm_configuration(
            db=db,
            config_id=params.config_id,
            user_id=params.user_id
        )
        
        if not db_config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        return _to_active_response(db_config)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.bind(tag=TAG).error(f"切换激活配置失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/llm-config-model-types", response_model=ApiResponseData)
async def list_model_types():
    """
    获取支持的模型类型列表
    
    不需要请求体
    """
    return {"model_types": [item.value for item in ModelTypeEnum]}


@router.post("/llm-config-client", response_model=ApiResponseData)
async def get_client_config(
    params: LLMConfigClientRequest,
    db: Session = Depends(get_sqlalchemy_db)
):
    """
    获取用于AI客户端的配置（供ai_client内部使用）
    
    返回格式：
    {
        "api_key": "...",
        "base_url": "...",
        "model": "...",
        ...
    }
    
    请求体示例:
    ```json
    {
        "user_id": null
    }
    ```
    """
    try:
        # 确保表存在
        _ensure_table_exists(db)
        
        logger.bind(tag=TAG).info(f"请求获取客户端配置 - user_id: {params.user_id}")
        
        config = get_llm_config_for_client(db, params.user_id)
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="未找到激活的配置，请先创建并激活一个配置"
            )
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取客户端配置失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
