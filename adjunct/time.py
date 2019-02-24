"""
Date/time utilities.
"""

import datetime


def date(timestamp, fmt="%Y-%m-%dT%H:%M:%S%z", tz=datetime.timezone.utc):
    """
    Formatting of SQLite timestamps.

    SQLite timestamps are taken to be in UTC. If you want them adjusted to
    another timezone, pass a `tzinfo` object representing that timezone in
    the `tz` parameter. The `fmt` parameter specifies a `strftime` date format
    string; it defaults to the `ISO 8601`_/`RFC 3339`_ date format.

    .. _ISO 8601: http://en.wikipedia.org/wiki/ISO_8601
    .. _RFC 3339: http://tools.ietf.org/html/rfc3339
    """
    dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=tz).strftime(fmt)
