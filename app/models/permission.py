from sqlalchemy import Column, Integer, String, Text
from app.models.base import Base

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))