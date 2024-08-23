from fastapi import APIRouter
from app.api.v1.endpoints import users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/user", tags=["users"])
