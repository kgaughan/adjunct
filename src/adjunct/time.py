"""Date/time utilities."""

import datetime as dt


def parse_dt(
    ts: str,
    tz: dt.tzinfo | None = dt.UTC,
) -> dt.datetime:
    """Parse an SQLite datetime, treating it as UTC by default.

    Args:
        ts: an SQLite timestamp string
        tz: the timezone to use, or `None` to treat it naively

    Returns:
        the parsed datetime.
    """
    parsed = dt.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
    return parsed if tz is None else parsed.replace(tzinfo=tz)


def to_iso_date(ts: str, tz: dt.tzinfo = dt.UTC) -> str:
    """Convert an SQLite timestamp string to [ISO 8601] format.

    [ISO 8601]: http://en.wikipedia.org/wiki/ISO_8601

    Args:
        ts: an SQLite timestamp string
        tz: a timezone object

    Returns:
        the same timestamp, but in ISO 8601 format.
    """
    return parse_dt(ts, tz).isoformat()
