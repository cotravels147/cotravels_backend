from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DirectChat(Base):
    __tablename__ = 'direct_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)