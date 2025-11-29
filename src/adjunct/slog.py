"""Simple structured logging with spans.

This module provides utilities for structured logging in JSON format, including
the ability to create logging spans that carry contextual metadata.

It builds on Python's built-in [logging][] module.

To configure logging to use structured logging, set up a logger with
`JSONFormatter`:

```python
import logging

from adjunct import slog


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
JSONFormatter.configure_handler(handler)
logger.addHandler(handler)
```

Both `slog.M` and `slog.span` can then be used to add structured metadata to
log records:

```python
logger.info(slog.M("User logged in", user="alice"))  # Log with metadata
with slog.span(request_id="12345", user_id="alice"):  # Log within a span
    logger.info(slog.M("User action", action="update_profile"))
```

`slog.M` and `slog.JSONFormatter` work together to produce JSON log records
that include the specified metadata and span context, but can both be used
independently if desired. Using `slog.M` will produce a stringified message
that includes the metadata in JSON, even without `slog.JSONFormatter`.

Note:
    The keys `spanId` and `parentSpanId` are reserved for span tracking and
    should not be used in metadata passed to `slog.M` or `slog.span`. They
    are named to match OpenTelemetry conventions.
"""

import base64
import collections
import json
import logging
import os
import threading
import typing as t

Scalar = str | int | float | bool | None


def _generate_span_id():
    return base64.b16encode(os.urandom(8)).decode("utf-8")


class _SpanStack(threading.local):
    """A thread-local stack of logging spans."""

    def __init__(self) -> None:
        super().__init__()
        self._stack: list[t.MutableMapping[str, Scalar]] = [
            collections.ChainMap({"spanId": _generate_span_id()}),
        ]

    def top(self) -> t.MutableMapping[str, Scalar]:
        return self._stack[-1]

    def extend(self, **kwargs: Scalar) -> None:
        """Add additional context to the current span."""
        self._stack[-1].update(kwargs)

    def __enter__(self) -> "_SpanStack":
        return self

    def __exit__(self, *_) -> None:
        self._stack.pop()

    def __call__(self, /, **kwargs: Scalar) -> "_SpanStack":
        top = self._stack[-1]
        ctx = collections.ChainMap(
            {"spanId": _generate_span_id(), "parentSpanId": top["spanId"]},
            kwargs,
            top,
        )
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

    def __init__(self, message: str, **metadata: Scalar) -> None:
        self.message = message
        self.metadata = metadata

    def __str__(self) -> str:
        if not self.metadata:
            return self.message
        ctx = span.top()
        combined = {**ctx, **self.metadata}
        return f"{self.message} | {json.dumps(combined)}"


class _SpanContextFilter(logging.Filter):
    """Populate log records with the active span context at emit time."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Capture the span context when the record is emitted, so async/queued
        # handlers will keep the original span data.
        record._adjunct_slog_ctx = span.top()
        return True


_span_context_filter = _SpanContextFilter()


class JSONFormatter(logging.Formatter):
    """A logging formatter that outputs JSON log records."""

    def format(self, record: logging.LogRecord) -> str:
        # Prefer span context captured at emit time (from SpanContextFilter),
        # with a fallback to the current span if SpanContextFilter is not used.
        ctx = getattr(record, "_adjunct_slog_ctx", span.top())
        record_dict: dict[str, Scalar] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
        }
        if isinstance(record.msg, M):
            chained = collections.ChainMap(record_dict, record.msg.metadata, ctx)
            record_dict["message"] = record.msg.message
        else:
            chained = collections.ChainMap(record_dict, ctx)
            record_dict["message"] = record.getMessage()
        if record.exc_info:
            record_dict["exception"] = self.formatException(record.exc_info)
        return json.dumps(dict(chained))

    @classmethod
    def configure_handler(cls, handler: logging.Handler) -> None:
        """Configure a logging handler to use JSONFormatter and SpanContextFilter.

        Args:
            handler: The logging handler to configure.
        """
        handler.setFormatter(cls())
        handler.addFilter(_span_context_filter)
