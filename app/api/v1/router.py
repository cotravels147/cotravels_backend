from fastapi import APIRouter
from app.api.v1.endpoints import users, friends, notifications

api_router = APIRouter()

api_router.include_router(users.router, prefix="/user", tags=["users"])
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])