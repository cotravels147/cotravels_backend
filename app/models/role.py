from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    group_user_roles = relationship("GroupUserRole", back_populates="role")