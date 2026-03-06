"""Tests for the logger module — JSON output, uvicorn access/error, context propagation."""

import json
import logging

import pytest

from {{ cookiecutter.project_slug }}.context import bind_context, clear_context
from {{ cookiecutter.project_slug }}.logger import setup_logging


@pytest.fixture(autouse=True)
def _reset_logging_and_context():
    """Restore logging and context state after every test."""
    yield
    clear_context()
    logging.root.handlers = []
    logging.root.setLevel(logging.WARNING)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True
        lg.setLevel(logging.NOTSET)


def _access_record() -> logging.LogRecord:
    """Return a uvicorn-style access log record."""
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='%s - "%s %s %s" %d',
        args=("127.0.0.1:9000", "GET", "/healthz", "HTTP/1.1", 200),
        exc_info=None,
    )


def _emit(logger_name: str, record: logging.LogRecord) -> None:
    for handler in logging.getLogger(logger_name).handlers:
        handler.handle(record)  # use handle(), not emit(), so filters (incl. _ContextFilter) run


def _capture_json(capsys) -> dict:
    out = capsys.readouterr().err.strip()
    assert out, "No output captured on stderr"
    return json.loads(out)


# ---------------------------------------------------------------------------
# Basic JSON output
# ---------------------------------------------------------------------------


def test_root_logger_emits_valid_json(capsys):
    setup_logging()
    logging.getLogger("test.basic").info("hello")
    data = _capture_json(capsys)
    assert data["message"] == "hello"
    assert data["level"] == "INFO"
    assert "timestamp" in data
    assert "logger" in data


def test_timestamp_has_utc_offset(capsys):
    setup_logging()
    logging.getLogger("test.ts").info("ts")
    data = _capture_json(capsys)
    assert data["timestamp"].endswith("+00:00"), f"Not UTC: {data['timestamp']}"


def test_service_field_included_when_provided(capsys):
    setup_logging(service="my-api")
    logging.getLogger("test.svc").info("svc")
    data = _capture_json(capsys)
    assert data["service"] == "my-api"


def test_service_field_absent_when_not_provided(capsys):
    setup_logging()
    logging.getLogger("test.nosvc").info("no svc")
    data = _capture_json(capsys)
    assert "service" not in data


def test_level_filter_suppresses_below_threshold(capsys):
    setup_logging(level="WARNING")
    logging.getLogger("test.filter").info("should be dropped")
    assert capsys.readouterr().err.strip() == ""


# ---------------------------------------------------------------------------
# Context propagation
# ---------------------------------------------------------------------------


def test_bound_context_fields_appear_in_root_log(capsys):
    setup_logging()
    bind_context(request_id="req-1", trace_id="tr-1")
    logging.getLogger("test.ctx").info("ctx log")
    data = _capture_json(capsys)
    assert data["request_id"] == "req-1"
    assert data["trace_id"] == "tr-1"


# ---------------------------------------------------------------------------
# uvicorn.error
# ---------------------------------------------------------------------------


def test_uvicorn_error_emits_valid_json(capsys):
    setup_logging()
    logging.getLogger("uvicorn.error").error("startup failed")
    data = _capture_json(capsys)
    assert data["message"] == "startup failed"
    assert data["level"] == "ERROR"
    assert data["logger"] == "uvicorn.error"


def test_uvicorn_error_includes_request_id_and_trace_id(capsys):
    setup_logging()
    bind_context(request_id="req-uv-err", trace_id="tr-uv-err")
    logging.getLogger("uvicorn.error").warning("oops")
    data = _capture_json(capsys)
    assert data["request_id"] == "req-uv-err"
    assert data["trace_id"] == "tr-uv-err"


def test_uvicorn_error_does_not_propagate():
    setup_logging()
    assert not logging.getLogger("uvicorn.error").propagate


# ---------------------------------------------------------------------------
# uvicorn.access
# ---------------------------------------------------------------------------


def test_uvicorn_access_emits_valid_json(capsys):
    setup_logging()
    _emit("uvicorn.access", _access_record())
    data = _capture_json(capsys)
    assert isinstance(data, dict)
    assert data["level"] == "INFO"


def test_uvicorn_access_message_is_http_request(capsys):
    setup_logging()
    _emit("uvicorn.access", _access_record())
    data = _capture_json(capsys)
    assert data["message"] == "HTTP request"


def test_uvicorn_access_has_structured_http_object(capsys):
    setup_logging()
    _emit("uvicorn.access", _access_record())
    data = _capture_json(capsys)
    http = data["http"]
    assert http["method"] == "GET"
    assert http["path"] == "/healthz"
    assert http["status"] == 200
    assert http["client"] == "127.0.0.1:9000"
    assert http["version"] == "HTTP/1.1"


def test_uvicorn_access_includes_request_id_and_trace_id(capsys):
    setup_logging()
    bind_context(request_id="req-access-1", trace_id="tr-access-1")
    _emit("uvicorn.access", _access_record())
    data = _capture_json(capsys)
    assert data["request_id"] == "req-access-1"
    assert data["trace_id"] == "tr-access-1"


def test_uvicorn_access_does_not_propagate():
    setup_logging()
    assert not logging.getLogger("uvicorn.access").propagate


def test_uvicorn_access_non_standard_args_does_not_crash(capsys):
    setup_logging()
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="some message",
        args=(),
        exc_info=None,
    )
    _emit("uvicorn.access", record)
    data = _capture_json(capsys)
    assert "http" not in data  # no structured http block
