from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String, Boolean
from sqlalchemy.orm import relationship
import datetime
from app.models.base import Base

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    image_url = Column(String(255))
    is_deleted = Column(Boolean, default=False, nullable=False)
    location = Column(String(255))
    trip_start_date = Column(DateTime)
    trip_end_date = Column(DateTime)

    user = relationship("User", back_populates="posts")