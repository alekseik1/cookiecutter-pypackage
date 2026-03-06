"""
JSON logging for FastAPI/Uvicorn, scripts, and workers.
Install `orjson` and `python-json-logger` before using this.

Usage:
    setup_logging(service="my-api")              # JSON to stdout
    setup_logging(level="DEBUG")                 # with a different level
    app.add_middleware(RequestContextMiddleware)  # auto request_id in FastAPI
    bind_context(user_id=42)                     # add fields to current context
    logger.info("ok", extra={"order_id": 1})     # extra fields → JSON automatically
    uvicorn.run(app, log_config=None)            # required, otherwise uvicorn resets logging config
"""

from __future__ import annotations

import logging
import sys
from datetime import UTC, datetime

from pythonjsonlogger.orjson import OrjsonFormatter

from .context import get_context


class _UtcJsonFormatter(OrjsonFormatter):
    """JsonFormatter with UTC timestamp and explicit offset (+00:00)."""

    def formatTime(self, record, datefmt=None):
        return datetime.fromtimestamp(record.created, tz=UTC).isoformat(timespec="seconds")


class _ContextFilter(logging.Filter):
    """Injects all fields from _ctx into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        for k, v in get_context().items():
            setattr(record, k, v)
        return True


class _UvicornAccessFormatter(_UtcJsonFormatter):
    """Unpacks uvicorn access log args into a structured http object."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if record.args and len(record.args) == 5:
            client, method, path, version, status = record.args
            log_record["http"] = {
                "client": client,
                "method": method,
                "path": path,
                "version": version,
                "status": status,
            }
            log_record["message"] = "HTTP request"
            record.args = ()
            record.msg = "HTTP request"


def setup_logging(level: str = "INFO", service: str | None = None) -> None:
    """Configure JSON logging for the entire application.

    Attaches a handler to root logger — covers all third-party libraries.
    Uvicorn loggers are configured explicitly since they set propagate=False by default.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    static = {"service": service} if service else {}
    ctx_filter = _ContextFilter()

    def make_handler(formatter: logging.Formatter) -> logging.Handler:
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(formatter)
        h.addFilter(ctx_filter)
        return h

    handler = make_handler(
        _UtcJsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "name": "logger", "asctime": "timestamp"},
            static_fields=static,
            json_ensure_ascii=False,
        )
    )
    access_handler = make_handler(
        _UvicornAccessFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "name": "logger", "asctime": "timestamp"},
            static_fields=static,
            json_ensure_ascii=False,
        )
    )

    logging.root.handlers = [handler]
    logging.root.setLevel(log_level)

    for name in ("uvicorn", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.handlers, lg.propagate = [handler], False
        lg.setLevel(log_level)

    uv_access = logging.getLogger("uvicorn.access")
    uv_access.handlers, uv_access.propagate = [access_handler], False
    uv_access.setLevel(logging.INFO)


# Example in starlette
'''
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RequestContextMiddleware(BaseHTTPMiddleware):
    """Binds request_id and trace_id to the context of each request."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        bind_context(
            request_id=request.headers.get("X-Request-ID") or str(uuid4()),
            trace_id=request.headers.get("X-Trace-ID") or str(uuid4()),
        )
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = _ctx.get().get("request_id", "")
            return response
        finally:
            clear_context()
'''
