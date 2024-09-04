from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime
from app.models.base import Base

class TravelPlan(Base):
    __tablename__ = 'travel_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="travel_plans")
    destinations = relationship("TravelPlanDestination", back_populates="travel_plan")
    itineraries = relationship("Itinerary", back_populates="travel_plan")
    hotel_bookings = relationship("HotelBooking", back_populates="travel_plan")