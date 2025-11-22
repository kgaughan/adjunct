"""Date/time utilities."""

import datetime


def date(
    dt: str,
    fmt: str = "%Y-%m-%dT%H:%M:%S%z",
    tz: datetime.timezone = datetime.UTC,
):
    """Format an SQLite timestamp.

    SQLite timestamps are taken to be in UTC. If you want them adjusted to
    another timezone, pass a `tzinfo` object representing that timezone in
    the `tz` parameter. The `fmt` parameter specifies a `strftime` date format
    string; it defaults to the [ISO 8601]/[RFC 3339] date format.

    [ISO 8601]: http://en.wikipedia.org/wiki/ISO_8601
    [RFC 3339]: http://tools.ietf.org/html/rfc3339

    Args:
        dt: an SQLite timestamp string
        fmt: a [datetime.datetime.strftime][] date format string
        tz: a timezone object

    Returns:
        The formatted time
    """
    return parse_dt(dt, tz).strftime(fmt)


def parse_dt(
    dt: str,
    tz: datetime.timezone | None = datetime.UTC,
) -> datetime.datetime:
    """Parse an SQLite datetime, treating it as UTC.

    Args:
        dt: an SQLite timestamp string
        tz: the timezone to use, or `None` to treat it naively

    Returns:
        the parsed datetime
    """
    parsed = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
    return parsed if tz is None else parsed.replace(tzinfo=tz)


def to_iso_date(dt: str) -> str:
    """Convert an SQLite timestamp string to [ISO 8601] format.

    [ISO 8601]: http://en.wikipedia.org/wiki/ISO_8601

    Args:
        dt: an SQLite timestamp string

    Returns:
        the same timestamp, but in ISO 8601 format.

    """
    return parse_dt(dt).isoformat()
