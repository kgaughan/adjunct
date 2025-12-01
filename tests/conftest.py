import pytest

from adjunct import fixtureutils

DISCOVER_FEEDS = b"""<!DOCTYPE html>
<html>
    <head>
        <link rel="alternate" type="application/rss+xml" title="RSS" href="/feeds/rss">
        <link rel="alternate" type="application/atom+xml" title="Atom" href="/feeds/atom">
    </head>
</html>
"""

DISCOVER_FEEDS_ANCHORS = b"""<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <a href="/feeds/rss">RSS Feed</a>
        <a href="/feeds/atom">Atom Feed</a>
        <a href="/feeds/rss.xml">RSS Feed</a>
        <a href="/feed.rdf">RDF Feed</a>
        <a href="/feed.xoxo">XOXO Feed</a>
        <a>Not a feed, not even a link</a>
    </body>
</html>
"""

META = b"""<!DOCTYPE html>
<html>
    <head>
        <link rel="foo" href="bar">
        <meta property="og:title" content="Example">
    </head>
</html>"""


def app(environ, start_response):
    status = "200 OK"
    headers = [("Content-Type", "text/html; charset=UTF-8")]
    match environ["PATH_INFO"]:
        case "/400":
            status = "400 Bad Request"
            body = [b"Bad Request"]
        case "/500":
            status = "500 Internal Server Error"
            body = [b"Internal Server Error"]
        case "/discoverfeeds":
            body = [DISCOVER_FEEDS]
        case "/discoveranchorfeeds":
            body = [DISCOVER_FEEDS_ANCHORS]
        case "/meta":
            headers = [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Link", "http://malformed.example.com/"),
                ("Link", '<http://example.com/>; rel="bar"'),
            ]
            body = [META]
        case _:
            headers = [("Content-Type", "text/plain; charset=UTF-8")]
            body = [b"Fixture App Response"]
    start_response(status, headers)
    return body


@pytest.fixture(scope="session")
def fixture_app():
    with fixtureutils.fixture(app) as addr:
        yield addr
