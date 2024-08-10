from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GroupChat(Base):
    __tablename__ = 'group_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)