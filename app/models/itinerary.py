from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.models.base import Base

class Itinerary(Base):
    __tablename__ = 'itineraries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    travel_plan_id = Column(Integer, ForeignKey('travel_plans.id'), nullable=False)
    day_number = Column(Integer, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    travel_plan = relationship("TravelPlan", back_populates="itineraries")
    activities = relationship("ItineraryActivity", back_populates="itinerary")
    group_chat_itineraries = relationship("GroupChatItinerary", back_populates="itinerary")