"""Input sanitization middleware — length limits and character validation.

Inspired by API Tester agent: input validation and SQL injection prevention.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

MAX_QUERY_LENGTH = 2000
MAX_TERM_LENGTH = 500
MAX_CATEGORY_LENGTH = 200
MAX_CHAT_MESSAGE_LENGTH = 2000

CONTROL_CHARS = set(chr(i) for i in range(0, 32)) - {"\n", "\r", "\t"}


class InputSanitizerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1_000_000:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"},
            )

        query_params = dict(request.query_params)
        for key, value in query_params.items():
            if not isinstance(value, str):
                continue
            if key in ("q", "message") and len(value) > MAX_QUERY_LENGTH:
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"'{key}' too long (max {MAX_QUERY_LENGTH})"},
                )

        return await call_next(request)
