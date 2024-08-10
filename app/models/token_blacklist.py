from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(500), nullable=False)
    blacklisted_at = Column(DateTime)