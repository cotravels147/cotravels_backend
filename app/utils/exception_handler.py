from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

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
                "message": f"{field_name.capitalize()} {message}",
            })

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "errors": detailed_errors
        })
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"message": "Database error occurred."},
    )

async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"errors": {"message": exc.detail}},
    )
