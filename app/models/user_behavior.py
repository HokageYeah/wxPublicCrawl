"""
用户行为数据模型
用于存储用户在桌面程序中的个人设置和行为偏好
"""
from sqlalchemy import Column, Integer, String, DateTime
from app.db.sqlalchemy_db import Base
from datetime import datetime


# 用户行为类型枚举
class BehaviorType:
    """用户行为类型常量"""
    # 下载路径保存行为
    SAVE_DOWNLOAD_PATH = "SAVE_DOWNLOAD_PATH"

    # 是否保存到本地（1: 是，2: 否）
    SAVE_TO_LOCAL = "SAVE_TO_LOCAL"

    # 是否上传到阿里云（1: 是，2: 否）
    UPLOAD_TO_ALIYUN = "UPLOAD_TO_ALIYUN"

    # 搜索历史
    SEARCH_HISTORY = "SEARCH_HISTORY"

    # 喜马拉雅下载路径保存行为
    XIMALAYA_DOWNLOAD_PATH = "XIMALAYA_DOWNLOAD_PATH"

    # 其他用户行为可以继续添加


class UserBehavior(Base):
    """用户行为表"""
    __tablename__ = "user_behavior"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(String(100), nullable=False, index=True, comment="用户ID（uin 或 nick_name）")
    behavior_type = Column(String(50), nullable=False, index=True, comment="行为类型")
    behavior_value = Column(String(1000), nullable=False, comment="行为值")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<UserBehavior(id={self.id}, user_id={self.user_id}, type={self.behavior_type}, value={self.behavior_value})>"

