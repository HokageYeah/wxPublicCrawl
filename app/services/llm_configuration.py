"""
LLM配置服务层
处理LLM配置的CRUD操作
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from loguru import logger
from app.models.llm_configuration import LLMConfiguration
from app.schemas.llm_configuration import (
    LLMConfigurationCreate,
    LLMConfigurationUpdate
)


TAG = "LLM_CONFIGURATION_SERVICE"


def mask_api_key(api_key: str) -> str:
    """
    脱敏API密钥
    
    Args:
        api_key: 原始API密钥
        
    Returns:
        str: 脱敏后的API密钥
    """
    if not api_key:
        return ""
    # 只保留前6位和后4位
    if len(api_key) <= 10:
        return api_key[:3] + "****"
    return api_key[:6] + "..." + api_key[-4:]


def create_llm_configuration(
    db: Session,
    config: LLMConfigurationCreate
) -> LLMConfiguration:
    """
    创建新的LLM配置
    
    Args:
        db: 数据库会话
        config: 配置数据
        
    Returns:
        LLMConfiguration: 创建的配置对象
    """
    try:
        # 如果设置为激活，需要先取消其他激活状态
        if config.is_active:
            _deactivate_all_configs(db, user_id=config.user_id)
        
        db_config = LLMConfiguration(**config.model_dump())
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        
        logger.bind(tag=TAG).info(
            f"创建LLM配置成功 - ID: {db_config.id}, "
            f"模型: {db_config.model_name}, 类型: {db_config.model_type}"
        )
        return db_config
        
    except Exception as e:
        db.rollback()
        logger.bind(tag=TAG).error(f"创建LLM配置失败: {e}")
        raise


def get_llm_configuration_by_id(
    db: Session,
    config_id: int,
    user_id: Optional[str] = None
) -> Optional[LLMConfiguration]:
    """
    根据ID获取LLM配置
    
    Args:
        db: 数据库会话
        config_id: 配置ID
        user_id: 用户ID（可选，用于权限控制）
        
    Returns:
        LLMConfiguration: 配置对象，如果不存在则返回None
    """
    try:
        query = db.query(LLMConfiguration).filter(LLMConfiguration.id == config_id)
        
        if user_id is not None:
            query = query.filter(
                or_(
                    LLMConfiguration.user_id == user_id,
                    LLMConfiguration.user_id == None  # None表示全局配置
                )
            )
        
        return query.first()
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取LLM配置失败: {e}")
        raise


def get_llm_configurations(
    db: Session,
    user_id: Optional[str] = None,
    model_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[LLMConfiguration], int]:
    """
    获取LLM配置列表
    
    Args:
        db: 数据库会话
        user_id: 用户ID（可选）
        model_type: 模型类型过滤（可选）
        is_active: 是否激活过滤（可选）
        skip: 跳过数量
        limit: 返回数量限制
        
    Returns:
        tuple: (配置列表, 总数)
    """
    try:
        query = db.query(LLMConfiguration)
        
        # 用户过滤：返回用户自己的配置 + 全局配置
        if user_id is not None:
            query = query.filter(
                or_(
                    LLMConfiguration.user_id == user_id,
                    LLMConfiguration.user_id == None
                )
            )
        
        # 模型类型过滤
        if model_type:
            query = query.filter(LLMConfiguration.model_type == model_type)
        
        # 激活状态过滤
        if is_active is not None:
            query = query.filter(LLMConfiguration.is_active == is_active)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        configs = query.order_by(LLMConfiguration.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.bind(tag=TAG).info(f"获取LLM配置列表 - 总数: {total}, 返回: {len(configs)}")
        return configs, total
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取LLM配置列表失败: {e}")
        raise


def update_llm_configuration(
    db: Session,
    config_id: int,
    config_update: LLMConfigurationUpdate,
    user_id: Optional[str] = None
) -> Optional[LLMConfiguration]:
    """
    更新LLM配置
    
    Args:
        db: 数据库会话
        config_id: 配置ID
        config_update: 更新数据
        user_id: 用户ID（可选，用于权限控制）
        
    Returns:
        LLMConfiguration: 更新后的配置对象，如果不存在则返回None
    """
    try:
        db_config = get_llm_configuration_by_id(db, config_id, user_id)
        
        if not db_config:
            logger.bind(tag=TAG).warning(f"配置不存在 - ID: {config_id}")
            return None
        
        # 如果设置为激活，需要先取消其他激活状态
        if config_update.is_active and not db_config.is_active:
            _deactivate_all_configs(db, user_id=db_config.user_id)
        
        # 更新字段
        update_data = config_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_config, key, value)
        
        db.commit()
        db.refresh(db_config)
        
        logger.bind(tag=TAG).info(f"更新LLM配置成功 - ID: {config_id}")
        return db_config
        
    except Exception as e:
        db.rollback()
        logger.bind(tag=TAG).error(f"更新LLM配置失败: {e}")
        raise


def delete_llm_configuration(
    db: Session,
    config_id: int,
    user_id: Optional[str] = None
) -> bool:
    """
    删除LLM配置
    
    Args:
        db: 数据库会话
        config_id: 配置ID
        user_id: 用户ID（可选，用于权限控制）
        
    Returns:
        bool: 是否删除成功
    """
    try:
        db_config = get_llm_configuration_by_id(db, config_id, user_id)
        
        if not db_config:
            logger.bind(tag=TAG).warning(f"配置不存在 - ID: {config_id}")
            return False
        
        db.delete(db_config)
        db.commit()
        
        logger.bind(tag=TAG).info(f"删除LLM配置成功 - ID: {config_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.bind(tag=TAG).error(f"删除LLM配置失败: {e}")
        raise


def get_active_llm_configuration(
    db: Session,
    user_id: Optional[str] = None
) -> Optional[LLMConfiguration]:
    """
    获取当前激活的LLM配置
    
    优先级：
    1. 用户的激活配置
    2. 全局的激活配置
    
    Args:
        db: 数据库会话
        user_id: 用户ID（可选）
        
    Returns:
        LLMConfiguration: 激活的配置对象，如果不存在则返回None
    """
    try:
        # 先查找用户的激活配置
        if user_id:
            config = db.query(LLMConfiguration).filter(
                and_(
                    LLMConfiguration.user_id == user_id,
                    LLMConfiguration.is_active == True
                )
            ).first()
            
            if config:
                logger.bind(tag=TAG).info(f"找到用户激活配置 - ID: {config.id}")
                return config
        
        # 再查找全局激活配置
        config = db.query(LLMConfiguration).filter(
            and_(
                LLMConfiguration.user_id == None,
                LLMConfiguration.is_active == True
            )
        ).first()
        
        if config:
            logger.bind(tag=TAG).info(f"找到全局激活配置 - ID: {config.id}")
        
        return config
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取激活配置失败: {e}")
        raise


def switch_active_llm_configuration(
    db: Session,
    config_id: int,
    user_id: Optional[str] = None
) -> Optional[LLMConfiguration]:
    """
    切换激活的LLM配置
    
    Args:
        db: 数据库会话
        config_id: 要激活的配置ID
        user_id: 用户ID（可选）
        
    Returns:
        LLMConfiguration: 新激活的配置对象
    """
    try:
        # 获取目标配置
        target_config = get_llm_configuration_by_id(db, config_id, user_id)
        
        if not target_config:
            logger.bind(tag=TAG).warning(f"目标配置不存在 - ID: {config_id}")
            return None
        
        # 取消同级别所有配置的激活状态
        _deactivate_all_configs(db, user_id=target_config.user_id)
        
        # 激活目标配置
        target_config.is_active = True
        db.commit()
        db.refresh(target_config)
        
        logger.bind(tag=TAG).info(f"切换激活配置成功 - 新ID: {config_id}")
        return target_config
        
    except Exception as e:
        db.rollback()
        logger.bind(tag=TAG).error(f"切换激活配置失败: {e}")
        raise


def _deactivate_all_configs(db: Session, user_id: Optional[str] = None) -> None:
    """
    取消所有配置的激活状态
    
    Args:
        db: 数据库会话
        user_id: 用户ID（如果为None，则取消全局配置的激活状态）
    """
    try:
        query = db.query(LLMConfiguration).filter(LLMConfiguration.is_active == True)
        
        if user_id is not None:
            query = query.filter(LLMConfiguration.user_id == user_id)
        else:
            query = query.filter(LLMConfiguration.user_id == None)
        
        configs = query.all()
        
        for config in configs:
            config.is_active = False
        
        logger.bind(tag=TAG).debug(f"取消激活状态 - 数量: {len(configs)}")
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"取消激活状态失败: {e}")
        raise


def get_llm_config_for_client(
    db: Session,
    user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    获取用于AI客户端的配置
    
    返回格式：
    {
        "api_key": "...",
        "base_url": "...",
        "model": "...",
        "temperature": ...,
        "max_tokens": ...,
        "enable_history": bool,
        "max_history": int,
        "system_prompt": "..."
    }
    
    Args:
        db: 数据库会话
        user_id: 用户ID（可选）
        
    Returns:
        Dict: 客户端配置字典，如果不存在则返回None
    """
    try:
        config = get_active_llm_configuration(db, user_id)
        
        if not config:
            logger.bind(tag=TAG).warning("未找到激活的LLM配置")
            return None
        
        client_config = {
            "api_key": config.ai_api_key,
            "base_url": config.ai_base_url,
            "model": config.model_name,
        }
        
        # 可选参数
        if config.temperature is not None:
            client_config["temperature"] = config.temperature / 100.0
        
        if config.max_tokens is not None:
            client_config["max_tokens"] = config.max_tokens
        
        if config.top_p is not None:
            client_config["top_p"] = config.top_p / 100.0
        
        if config.enable_history:
            client_config["enable_history"] = True
            client_config["max_history"] = config.max_history
        
        if config.system_prompt:
            client_config["system_prompt"] = config.system_prompt
        
        logger.bind(tag=TAG).info(
            f"获取客户端配置 - 模型: {config.model_name}, "
            f"类型: {config.model_type}"
        )
        
        return client_config
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取客户端配置失败: {e}")
        raise

