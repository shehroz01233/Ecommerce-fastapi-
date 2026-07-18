import time
import uuid
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ecommerce")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        logger.info(f"[{request_id}] {request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.error(f"[{request_id}] {request.method} {request.url.path} -> ERROR ({duration}ms): {str(exc)}")
            raise

        duration = round((time.time() - start_time) * 1000, 2)
        status = response.status_code
        level = logging.WARNING if status >= 400 else logging.INFO
        logger.log(level, f"[{request_id}] {request.method} {request.url.path} -> {status} ({duration}ms)")

        response.headers["X-Response-Time"] = f"{duration}ms"
        return response


class SlowRequestMiddleware(BaseHTTPMiddleware):
    SLOW_THRESHOLD_MS = 3000

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        if duration_ms > self.SLOW_THRESHOLD_MS:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                f"[{request_id}] SLOW REQUEST: {request.method} {request.url.path} took {duration_ms:.0f}ms"
            )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    MAX_BODY_SIZE = 5 * 1024 * 1024
    SKIP_METHODS = {"GET", "HEAD", "OPTIONS", "DELETE"}

    async def dispatch(self, request: Request, call_next):
        if request.method in self.SKIP_METHODS:
            return await call_next(request)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(f"[{request_id}] Body too large: {content_length} bytes")
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large. Maximum size is 5MB."}
            )
        return await call_next(request)
