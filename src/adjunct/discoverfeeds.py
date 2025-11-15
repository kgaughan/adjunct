"""
Feed discovery.
"""


from . import discovery

__all__ = ["discover_feeds"]


# Acceptable feed  types, sorted by priority.
ACCEPTABLE = ["application/atom+xml", "application/rdf+xml", "application/rss+xml"]

# Used when ordering feeds.
ORDER = {mimetype: i_type for i_type, mimetype in enumerate(ACCEPTABLE)}

GUESSES = {
    "application/rss+xml": (".rss", "rss.xml", "/rss", "/rss/", "/feed/"),
    "application/rdf+xml": (".rdf", "rdf.xml", "/rdf", "/rdf/"),
    "application/atom+xml": (".atom", "atom.xml", "/atom", "/atom/"),
}


class FeedExtractor(discovery.Extractor):
    """
    Extract any link or anchor elements that look like they might refer to
    feeds.
    """

    def __init__(self, base: str):
        super().__init__(base)
        self.anchor = None
        self.added: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag.lower() == "a" and self.anchor is None:
            fixed_attrs = discovery.fix_attributes(attrs)
            if "href" in fixed_attrs:
                fixed_attrs["@data"] = ""
                feed_type = self.guess_feed_type(fixed_attrs["href"])
                if feed_type in ACCEPTABLE:
                    fixed_attrs.setdefault("type", feed_type)
                    fixed_attrs.setdefault("rel", "feed")
                    self.anchor = fixed_attrs
        else:
            super().handle_starttag(tag, attrs)

    def handle_data(self, data: str):
        # We only use the interstitial text as the title if none was provided
        # on the anchor element itself.
        if self.anchor is not None and "title" not in self.anchor:
            self.anchor["@data"] += data

    def handle_endtag(self, tag: str):
        if tag.lower() == "a" and self.anchor is not None:
            self.anchor.setdefault("title", self.anchor["@data"])
            del self.anchor["@data"]
            self.append(self.anchor)
            self.anchor = None
        else:
            super().handle_endtag(tag)

    def guess_feed_type(self, href: str) -> str | None:
        """
        Guess the MIME type of a link based off of its ending.
        """
        # Reasonable assumption: we're dealing with <a> elements, and by this
        # time, we should've encountered any <base> elements we care about.
        href = self.fix_href(href)
        return next(
            (mimetype for mimetype, endings in GUESSES.items() if href.lower().endswith(endings)),
            None,
        )

    def append(self, attrs: dict[str, str]):
        if (
            attrs["rel"] in ("alternate", "feed")
            and "type" in attrs
            and attrs["type"].lower() in ACCEPTABLE
            and "href" in attrs
            and attrs["href"] not in self.added
        ):
            del attrs["rel"]
            super().append(attrs)
            self.added.add(attrs["href"])


def discover_feeds(url: str) -> list:
    """
    Discover any feeds at the given URL.
    """
    links, _ = discovery.fetch_meta(url, FeedExtractor)
    return sorted(links, key=(lambda feed: ORDER[feed["type"]]))
