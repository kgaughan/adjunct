"""
Date/time utilities.
"""

import datetime


def date(timestamp, fmt=None, tz=None):
    """
    Formatting of SQLite timestamps.

    SQLite timestamps are taken to be in UTC. If you want them adjusted to
    another timezone, pass a `tzinfo` object representing that timezone in
    the `tz` parameter. The `fmt` parameter specifies a `strftime` date format
    string; it defaults to the `ISO 8601`_/`RFC 3339`_ date format.

    .. _ISO 8601: http://en.wikipedia.org/wiki/ISO_8601
    .. _RFC 3339: http://tools.ietf.org/html/rfc3339
    """
    if fmt is None:
        fmt = '%Y-%m-%dT%H:%M:%S' + ('Z' if tz is None else '%z')
    dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    if tz is not None:
        dt = dt.astimezone(tz)
    return dt.strftime(fmt)
