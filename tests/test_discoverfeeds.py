from adjunct import discoverfeeds


def test_discover_feeds(fixture_app):
    feeds = discoverfeeds.discover_feeds(f"{fixture_app}discoverfeeds")
    # Note: feeds are returned in priority order.
    assert feeds == [
        {"type": "application/atom+xml", "title": "Atom", "href": f"{fixture_app}feeds/atom"},
        {"type": "application/rss+xml", "title": "RSS", "href": f"{fixture_app}feeds/rss"},
    ]


def test_discover_feeds_anchors(fixture_app):
    feeds = discoverfeeds.discover_feeds(f"{fixture_app}discoveranchorfeeds")
    # Note: feeds are returned in priority order.
    assert feeds == [
        {"type": "application/atom+xml", "title": "Atom Feed", "href": f"{fixture_app}feeds/atom"},
        {"type": "application/rdf+xml", "title": "RDF Feed", "href": f"{fixture_app}feed.rdf"},
        {"type": "application/rss+xml", "title": "RSS Feed", "href": f"{fixture_app}feeds/rss"},
        {"type": "application/rss+xml", "title": "RSS Feed", "href": f"{fixture_app}feeds/rss.xml"},
    ]
