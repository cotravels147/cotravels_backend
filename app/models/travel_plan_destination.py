from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class TravelPlanDestination(Base):
    __tablename__ = 'travel_plan_destinations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    travel_plan_id = Column(Integer, ForeignKey('travel_plans.id'), nullable=False)
    destination = Column(String(255), nullable=False)
    arrival_date = Column(DateTime, nullable=False)
    departure_date = Column(DateTime, nullable=False)
    notes = Column(Text)

    travel_plan = relationship("TravelPlan", back_populates="destinations")