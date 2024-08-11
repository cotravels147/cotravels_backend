from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
import datetime
from app.models.base import Base

class GroupChat(Base):
    __tablename__ = 'group_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
