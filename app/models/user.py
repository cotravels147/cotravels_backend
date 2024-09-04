from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, Text
from sqlalchemy.orm import relationship, deferred
import datetime
from app.models.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = deferred(Column(String(255), nullable=False))
    phone_number = Column(String(50), nullable=False)
    profile_picture = deferred(Column(String(255), nullable=True))
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum('male', 'female', 'other', name='gender_enum'), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    country = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    verification_status = Column(String(50), default="unverified", nullable=False)
    bio = Column(Text)
    travel_preferences = Column(Text)
    languages_spoken = Column(Text)

    posts = relationship("Post", back_populates="user")
    travel_plans = relationship("TravelPlan", back_populates="user")
    travel_tips = relationship("TravelTip", back_populates="user")
    hotel_bookings = relationship("HotelBooking", back_populates="user")
    sent_friend_requests = relationship("FriendRequest", foreign_keys="FriendRequest.sender_id", back_populates="sender")
    received_friend_requests = relationship("FriendRequest", foreign_keys="FriendRequest.receiver_id", back_populates="receiver")
    friends = relationship("Friend", foreign_keys="Friend.user_id", back_populates="user")
    jwt_sessions = relationship("JwtSession", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")