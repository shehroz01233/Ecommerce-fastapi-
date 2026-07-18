import time
import uuid
import logging
from fastapi import Request
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
