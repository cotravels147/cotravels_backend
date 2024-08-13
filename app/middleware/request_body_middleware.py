from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Middleware to add request data to RequestValidationError
class RequestBodyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            body = await request.json()
        except Exception:
            body = {}
        request.state.body = body
        return await call_next(request)