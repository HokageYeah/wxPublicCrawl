from sqlalchemy import Column, Integer, String
from app.db.sqlalchemy_db import Base

class SearchTag(Base):
    __tablename__ = "search_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    def __repr__(self):
        return f"<SearchTag(name='{self.name}')>"
