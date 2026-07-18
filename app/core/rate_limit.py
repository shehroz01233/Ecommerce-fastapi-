from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from ..core.redis import redis_manager


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_limit: int = 100, default_window: int = 60):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        self.path_limits = {
            "/api/auth/login": {"limit": 10, "window": 60},
            "/api/auth/register": {"limit": 5, "window": 300},
            "/api/cart/": {"limit": 30, "window": 60},
            "/api/orders/": {"limit": 20, "window": 60},
        }

    def get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        if not redis_manager.connected:
            return await call_next(request)

        client_ip = self.get_client_ip(request)
        path = request.url.path

        limit_config = self.path_limits.get(path, {
            "limit": self.default_limit,
            "window": self.default_window
        })

        rate_key = f"rate_limit:{client_ip}:{path}"
        current_count = redis_manager.increment_rate_limit(rate_key, limit_config["window"])

        if current_count > limit_config["limit"]:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit_config["limit"])
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit_config["limit"] - current_count))
        return response
