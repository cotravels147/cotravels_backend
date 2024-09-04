from sqlalchemy import Column, Integer, ForeignKey, String, Text, Time
from sqlalchemy.orm import relationship
from app.models.base import Base

class ItineraryActivity(Base):
    __tablename__ = 'itinerary_activities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    itinerary_id = Column(Integer, ForeignKey('itineraries.id'), nullable=False)
    activity_name = Column(String(255), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String(255))
    notes = Column(Text)

    itinerary = relationship("Itinerary", back_populates="activities")