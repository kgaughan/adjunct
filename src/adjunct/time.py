"""
Date/time utilities.
"""

import datetime


def date(
    dt: str,
    fmt: str = "%Y-%m-%dT%H:%M:%S%z",
    tz: datetime.timezone = datetime.UTC,
):
    """Formatting of SQLite timestamps.

    SQLite timestamps are taken to be in UTC. If you want them adjusted to
    another timezone, pass a `tzinfo` object representing that timezone in
    the `tz` parameter. The `fmt` parameter specifies a `strftime` date format
    string; it defaults to the [ISO 8601]/[RFC 3339] date format.

    [ISO 8601]: http://en.wikipedia.org/wiki/ISO_8601
    [RFC 3339]: http://tools.ietf.org/html/rfc3339
    """
    return parse_dt(dt, tz).strftime(fmt)


def parse_dt(
    dt: str,
    tz: datetime.timezone = datetime.UTC,
) -> datetime.datetime:
    """Parse an SQLite datetime, treating it as UTC.

    If you want it treated naively, pass `None` as the timezone.
    """
    parsed = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
    return parsed if tz is None else parsed.replace(tzinfo=tz)


def to_iso_date(dt: str) -> str:
    return parse_dt(dt).isoformat()
