"""Simple structured logging with spans.

This module provides utilities for structured logging in JSON format, including
the ability to create logging spans that carry contextual metadata.

It builds on Python's built-in [logging][] module.
"""

import base64
import json
import logging
import os
import threading


def _generate_span_id():
    return base64.b16encode(os.urandom(8)).decode("utf-8")


class _SpanStack(threading.local):
    """A thread-local stack of logging spans."""

    def __init__(self):
        super().__init__()
        self._stack: list[dict[str, str]] = [{"spanId": _generate_span_id()}]

    def top(self) -> dict[str, str]:
        return self._stack[-1]

    def extend(self, **kwargs: str) -> None:
        """Add additional context to the current span."""
        self._stack[-1].update(kwargs)

    def __enter__(self) -> "_SpanStack":
        return self

    def __exit__(self, *_) -> None:
        self._stack.pop()

    def __call__(self, /, **kwargs) -> "_SpanStack":
        top = self._stack[-1]
        ctx = {**top, **kwargs, "spanId": _generate_span_id(), "parentSpanId": top["spanId"]}
        self._stack.append(ctx)
        return self


span = _SpanStack()
"""A context manager for logging spans.

Examples:
    >>> with slog.span(request_id="12345", user_id="alice"):
    ...    logger.info(slog.M("User action", action="update_profile"))
"""


class M:
    """A message with some attached metaadata for structured logging.

    When stringified, this produces a JSON-like string that can be parsed by log processors.

    If used with JSONFormatter, it'll merge the metadata into the log record.

    Args:
        message: The main log message.
        **metadata: Additional key-value pairs to attach to the log record.
    """

    __slots__ = ("message", "metadata")

    def __init__(self, message: str, **metadata: str) -> None:
        self.message = message
        self.metadata = metadata

    def __str__(self) -> str:
        if not self.metadata:
            return self.message
        ctx = span.top()
        combined = {**ctx, **self.metadata}
        return f"{self.message} | {json.dumps(combined)}"


class JSONFormatter(logging.Formatter):
    """A logging formatter that outputs JSON log records."""

    def format(self, record: logging.LogRecord) -> str:
        record_dict: dict[str, str | dict[str, str]] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            **span.top(),
        }
        if isinstance(record.msg, M):
            record_dict.update(record.msg.metadata)
            record_dict["message"] = record.msg.message
        else:
            record_dict["message"] = record.getMessage()
        if record.exc_info:
            record_dict["exception"] = self.formatException(record.exc_info)
        return json.dumps(record_dict)


def get_logger(
    name: str,
    level: int = logging.INFO,
    handler: logging.Handler | None = None,
) -> logging.Logger:
    """Get a structured logger with JSON formatting.

    Args:
        name: The name of the logger.
        level: The logging level.
        handler: An optional logging handler. If not provided, a StreamHandler is used.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if handler is None:  # pragma: no cover
        handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger
