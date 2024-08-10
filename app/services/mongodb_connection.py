from motor.motor_asyncio import AsyncIOMotorClient
import os

# Environment variables for MongoDB credentials
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB")

client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DB]

# Dependency
def get_mongo_db():
    return db