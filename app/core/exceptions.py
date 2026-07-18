import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from jose import JWTError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("ecommerce")


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] HTTP {exc.status_code}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": request_id}
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"[{request_id}] DB Integrity Error: {str(exc)}")
        return JSONResponse(
            status_code=409,
            content={"detail": "Data conflict - resource may already exist", "request_id": request_id}
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.critical(f"[{request_id}] DB Operational Error: {str(exc)}")
        return JSONResponse(
            status_code=503,
            content={"detail": "Database temporarily unavailable", "request_id": request_id}
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"[{request_id}] DB Error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error occurred", "request_id": request_id}
        )

    @app.exception_handler(JWTError)
    async def jwt_error_handler(request: Request, exc: JWTError):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid authentication token", "request_id": request_id}
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Validation Error: {str(exc)}")
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc), "request_id": request_id}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        logger.critical(f"[{request_id}] Unhandled Error: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id}
        )
