import typing as tp
from contextvars import ContextVar

_ctx: ContextVar[dict[str, tp.Any] | None] = ContextVar("_ctx", default=None)


def bind_context(**fields: tp.Any) -> None:
    _ctx.set({**(_ctx.get() or {}), **fields})


def clear_context() -> None:
    _ctx.set({})


def get_context() -> dict[str, tp.Any]:
    return _ctx.get() or {}
