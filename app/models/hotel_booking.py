from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.models.base import Base

class HotelBooking(Base):
    __tablename__ = 'hotel_bookings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    travel_plan_id = Column(Integer, ForeignKey('travel_plans.id'), nullable=False)
    hotel_name = Column(String(255), nullable=False)
    booking_reference = Column(String(255), nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    booking_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="hotel_bookings")
    travel_plan = relationship("TravelPlan", back_populates="hotel_bookings")