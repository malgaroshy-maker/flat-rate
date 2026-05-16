"""In-memory sliding window rate limiter.

Inspired by API Tester agent: rate limiting and abuse prevention.
"""

from __future__ import annotations

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

INITIAL_WINDOW_SIZE = 30  # requests
INITIAL_WINDOW_SECONDS = 60  # seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = INITIAL_WINDOW_SIZE, window_seconds: int = INITIAL_WINDOW_SECONDS):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        now = time.time()
        key = f"{request.client.host if request.client else 'unknown'}:{request.url.path}"

        window = self._windows[key]
        cutoff = now - self.window_seconds
        self._windows[key] = [t for t in window if t > cutoff]

        if len(self._windows[key]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(self.window_seconds)},
            )

        self._windows[key].append(now)
        return await call_next(request)
