from adjunct import discoverfeeds, fixtureutils


def app_discover_feeds(environ, start_response):  # noqa: ARG001
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
    ]
    start_response("200 OK", headers)
    return [
        b"""<!DOCTYPE html>
<html>
    <head>
        <link rel="alternate" type="application/rss+xml" title="RSS" href="/feeds/rss">
        <link rel="alternate" type="application/atom+xml" title="Atom" href="/feeds/atom">
    </head>
</html>"""
    ]


def test_discover_feeds():
    with fixtureutils.fixture(app_discover_feeds) as addr:
        feeds = discoverfeeds.discover_feeds(addr)
        # Note: feeds are returned in priority order.
        assert feeds == [
            {"type": "application/atom+xml", "title": "Atom", "href": f"{addr}feeds/atom"},
            {"type": "application/rss+xml", "title": "RSS", "href": f"{addr}feeds/rss"},
        ]


def app_discover_feeds_anchors(environ, start_response):  # noqa: ARG001
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
    ]
    start_response("200 OK", headers)
    return [
        b"""<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <a href="/feeds/rss">RSS Feed</a>
        <a href="/feeds/atom">Atom Feed</a>
        <a href="/feeds/rss.xml">RSS Feed</a>
        <a href="/feed.rdf">RDF Feed</a>
        <a href="/feed.xoxo">XOXO Feed</a>
        <a>Not a feed, not even a link</a>
</html>"""
    ]


def test_discover_feeds_anchors():
    with fixtureutils.fixture(app_discover_feeds_anchors) as addr:
        feeds = discoverfeeds.discover_feeds(addr)
        # Note: feeds are returned in priority order.
        assert feeds == [
            {"type": "application/atom+xml", "title": "Atom Feed", "href": f"{addr}feeds/atom"},
            {"type": "application/rdf+xml", "title": "RDF Feed", "href": f"{addr}feed.rdf"},
            {"type": "application/rss+xml", "title": "RSS Feed", "href": f"{addr}feeds/rss"},
            {"type": "application/rss+xml", "title": "RSS Feed", "href": f"{addr}feeds/rss.xml"},
        ]
