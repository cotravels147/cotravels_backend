from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    image_url = Column(String(255))
    is_deleted = Column(Boolean, default=False)