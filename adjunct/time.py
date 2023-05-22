"""
Date/time utilities.
"""

import datetime


def date(dt, fmt="%Y-%m-%dT%H:%M:%S%z", tz=datetime.timezone.utc):
    """
    Formatting of SQLite timestamps.

    SQLite timestamps are taken to be in UTC. If you want them adjusted to
    another timezone, pass a `tzinfo` object representing that timezone in
    the `tz` parameter. The `fmt` parameter specifies a `strftime` date format
    string; it defaults to the `ISO 8601`_/`RFC 3339`_ date format.

    .. _ISO 8601: http://en.wikipedia.org/wiki/ISO_8601
    .. _RFC 3339: http://tools.ietf.org/html/rfc3339
    """
    return parse_dt(dt, tz).strftime(fmt)


def parse_dt(dt, tz=datetime.timezone.utc):
    """
    Parse an SQLite datetime, treating it as UTC.

    If you want it treated naively, pass `None` as the timezone.
    """
    parsed = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    return parsed if tz is None else parsed.replace(tzinfo=tz)


def to_iso_date(dt):
    return parse_dt(dt).isoformat()
