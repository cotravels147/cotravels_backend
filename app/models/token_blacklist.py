from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), unique=True, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)