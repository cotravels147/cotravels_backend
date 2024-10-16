from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.utils.exception_handler import register_exception_handlers
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.api.v1.router import api_router
from app.core.config import settings

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all exception handlers
register_exception_handlers(app)

# Mount the static folder to serve images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the router from your routes
app.include_router(api_router, prefix=settings.API_STR)

@app.get("/")
async def root():
    html_content = """
    <html>
        <head>
            <title>Welcome</title>
        </head>
        <body>
            <div style="margin-top:10vmin; margin-left:auto; margin-right:auto; width:50%;">
                <h1 style="text-align:center;">Welcome to CoTravels!</h1>
                <img style="display:block; margin-left:auto; margin-right:auto; width:60%;"src="/static/website_resources/logo-01.jpg">
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)