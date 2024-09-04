from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class GroupUserRole(Base):
    __tablename__ = 'group_user_roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('group_chats.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    group_chat = relationship("GroupChat", back_populates="group_user_roles")
    user = relationship("User")
    role = relationship("Role", back_populates="group_user_roles")