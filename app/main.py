from fastapi import FastAPI
from app.utils.exception_handler import register_exception_handlers
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.api.v1.router import api_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Register all exception handlers
register_exception_handlers(app)

# Mount the static folder to serve images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the router from your routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to CoTravels"}