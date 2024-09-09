import logging
import os
import traceback
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

# Directory for log files
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# General exception log setup
logging.basicConfig(
    filename=os.path.join(LOG_DIR, f"general_errors_{datetime.now().strftime('%Y-%m-%d')}.log"),
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# SQLAlchemy exception log setup
db_log_handler = logging.FileHandler(os.path.join(LOG_DIR, f"database_errors_{datetime.now().strftime('%Y-%m-%d')}.log"))
db_log_handler.setLevel(logging.ERROR)
db_log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
db_logger = logging.getLogger("db_logger")
db_logger.addHandler(db_log_handler)
db_logger.setLevel(logging.ERROR)

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    detailed_errors = []

    for error in errors:
        error_location = error["loc"]
        field_name = (error_location[-1])  # Last part of the location is the field name
        message = error["msg"].lower()
        if field_name == "body":
            detailed_errors.append({
                "required": "Request body",
                "message": "Please send required data in request body"
            })
        else:
            detailed_errors.append({
                "required": field_name,
                "message": f"{field_name} {message}",
            })

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "errors": detailed_errors
        })
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # Log the database error
    error_details = f"Database error: {str(exc)}\n{traceback.format_exc()}"
    db_logger.error(error_details)

    return JSONResponse(
        status_code=500,
        content={"message": "Database error occurred."},
    )

async def general_exception_handler(request: Request, exc: Exception):
    # Log the general unexpected error
    error_details = f"Unexpected error: {str(exc)}\n{traceback.format_exc()}"
    logging.error(error_details)
    
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"errors": {"message": exc.detail}},
    )
