from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
import datetime
from app.models.base import Base

class JwtSession(Base):
    __tablename__ = 'jwt_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(512), nullable=False)
    issued_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_accessed_at = Column(DateTime)