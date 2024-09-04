from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.models.base import Base

class GroupChat(Base):
    __tablename__ = 'group_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime)

    creator = relationship("User", foreign_keys=[created_by])
    group_user_roles = relationship("GroupUserRole", back_populates="group_chat")
    group_chat_itineraries = relationship("GroupChatItinerary", back_populates="group_chat")