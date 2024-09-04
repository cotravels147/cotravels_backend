from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.models.base import Base

class GroupChatItinerary(Base):
    __tablename__ = 'group_chat_itineraries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_chat_id = Column(Integer, ForeignKey('group_chats.id'), nullable=False)
    itinerary_id = Column(Integer, ForeignKey('itineraries.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    group_chat = relationship("GroupChat", back_populates="group_chat_itineraries")
    itinerary = relationship("Itinerary", back_populates="group_chat_itineraries")