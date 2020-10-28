"""
Feed discovery.
"""


from . import discovery


__all__ = ["discover_feeds"]


# Acceptable feed  types, sorted by priority.
ACCEPTABLE = ["application/atom+xml", "application/rdf+xml", "application/rss+xml"]

# Used when ordering feeds.
ORDER = dict((mimetype, i_type) for i_type, mimetype in enumerate(ACCEPTABLE))

GUESSES = {
    "application/rss+xml": (".rss", "rss.xml", "/rss", "/rss/", "/feed/"),
    "application/rdf+xml": (".rdf", "rdf.xml", "/rdf", "/rdf/"),
    "application/atom+xml": (".atom", "atom.xml", "/atom", "/atom/"),
}


# pylint: disable-msg=R0904
class FeedExtractor(discovery.Extractor):
    """
    Extract any link or anchor elements that look like they might refer to
    feeds.
    """

    def __init__(self, base):
        super().__init__(base)
        self.anchor = None
        self.added = set()

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a" and self.anchor is None:
            attrs = discovery.fix_attributes(attrs)
            if "href" in attrs:
                attrs["@data"] = ""
                attrs.setdefault("type", self.guess_feed_type(attrs["href"]))
                if attrs["type"] in ACCEPTABLE:
                    attrs.setdefault("rel", "feed")
                    self.anchor = attrs
        else:
            super().handle_starttag(tag, attrs)

    def handle_data(self, data):
        # We only use the interstitial text as the title if none was provided
        # on the anchor element itself.
        if self.anchor is not None and "title" not in self.anchor:
            self.anchor["@data"] += data

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.anchor is not None:
            self.anchor.setdefault("title", self.anchor["@data"])
            del self.anchor["@data"]
            self.append(self.anchor)
            self.anchor = None
        else:
            super().handle_endtag(tag)
            # Force scanning of the whole document.
            self.finished = False

    def guess_feed_type(self, href):
        """
        Guess the MIME type of a link based off of its ending.
        """
        # Reasonable assumption: we're dealing with <a> elements, and by this
        # time, we should've encountered any <base> elements we care about.
        href = self.fix_href(href)
        for mimetype, endings in GUESSES.items():
            if href.lower().endswith(endings):
                return mimetype
        return None

    def append(self, attrs):
        if attrs["rel"] in ("alternate", "feed"):
            if "type" in attrs and attrs["type"].lower() in ACCEPTABLE:
                if "href" in attrs and attrs["href"] not in self.added:
                    del attrs["rel"]
                    super().append(attrs)
                    self.added.add(attrs["href"])


def discover_feeds(url):
    """
    Discover any feeds at the given URL.
    """
    return sorted(
        discovery.fetch_links(url, FeedExtractor),
        key=(lambda feed: ORDER[feed["type"]]),
    )
