import json
import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import settings

logger = logging.getLogger("app.http")

SENSITIVE_FIELDS = {
    "password",
    "current_password",
    "new_password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "client_secret",
    "authorization",
    "cookie",
    "set-cookie",
    "api_key",
}

MAX_LOG_BODY_BYTES = 8 * 1024


def redact_sensitive_data(value: object) -> object:
    """Recursively redact sensitive fields from JSON data."""
    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED]"
                if key.lower() in SENSITIVE_FIELDS
                else redact_sensitive_data(item)
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [redact_sensitive_data(item) for item in value]

    return value


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        # Only inspect JSON request bodies in local development.
        if settings.app_env == "local":
            content_type = request.headers.get("content-type", "")
            content_length = request.headers.get("content-length", "")

            if (
                content_type.startswith("application/json")
                and content_length.isdigit()
                and int(content_length) <= MAX_LOG_BODY_BYTES
            ):
                try:
                    body = await request.json()
                    safe_body = redact_sensitive_data(body)

                    logger.debug(
                        "HTTP request body",
                        extra={
                            "request_id": request_id,
                            "method": request.method,
                            "path": request.url.path,
                            "body": json.dumps(safe_body),
                        },
                    )
                except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                    logger.debug(
                        "Request body omitted because JSON parsing failed",
                        extra={"request_id": request_id},
                    )

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "HTTP request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                },
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "HTTP request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response
