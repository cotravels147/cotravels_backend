from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.services.mysql_connection import get_db
from app.api.v1.routes import api_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Mount the static folder to serve images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the router from your routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}