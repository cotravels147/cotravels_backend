from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "CoTravels"
    API_STR: str = "/api"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://vite-pro-beta.vercel.app",
        "https://cotravels.in",
    ]

    # MySQL settings
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_DB: str

    # MongoDB settings
    MONGODB_URI: str
    MONGODB_DB: str

    # JWT settings
    JWT_SECRET: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()