from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/brands/")
async def read_items():
    return {"brands": ["Porche", "Jaguar", "BMW"]}