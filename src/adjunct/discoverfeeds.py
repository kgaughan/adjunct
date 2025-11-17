"""
Feed discovery.
"""

import typing as t

from . import discovery

__all__ = ["discover_feeds"]


# Acceptable feed  types, sorted by priority.
_ACCEPTABLE = ["application/atom+xml", "application/rdf+xml", "application/rss+xml"]

# Used when ordering feeds.
_ORDER = {mimetype: i_type for i_type, mimetype in enumerate(_ACCEPTABLE)}

_GUESSES = {
    "application/rss+xml": (".rss", "rss.xml", "/rss", "/rss/", "/feed/"),
    "application/rdf+xml": (".rdf", "rdf.xml", "/rdf", "/rdf/"),
    "application/atom+xml": (".atom", "atom.xml", "/atom", "/atom/"),
}


class _FeedExtractor(discovery.Extractor):
    """
    Extract any link or anchor elements that look like they might refer to
    feeds.
    """

    def __init__(self, base: str):
        super().__init__(base)
        self.anchor: dict[str, str] | None = None
        self.added: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag.lower() == "a" and self.anchor is None:
            fixed_attrs = discovery._fix_attributes(attrs)
            if "href" in fixed_attrs:
                fixed_attrs["@data"] = ""
                feed_type = self.guess_feed_type(fixed_attrs["href"])
                if feed_type in _ACCEPTABLE:
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
            self._append(self.anchor)
            self.anchor = None
        else:
            super().handle_endtag(tag)

    def guess_feed_type(self, href: str) -> str | None:
        """
        Guess the MIME type of a link based off of its ending.
        """
        # Reasonable assumption: we're dealing with <a> elements, and by this
        # time, we should've encountered any <base> elements we care about.
        href = self._fix_href(href)
        return next(
            (mimetype for mimetype, endings in _GUESSES.items() if href.lower().endswith(endings)),
            None,
        )

    def _append(self, attrs: dict[str, str]):
        if (
            attrs["rel"] in ("alternate", "feed")
            and "type" in attrs
            and attrs["type"].lower() in _ACCEPTABLE
            and "href" in attrs
            and attrs["href"] not in self.added
        ):
            del attrs["rel"]
            super()._append(attrs)
            self.added.add(attrs["href"])


def discover_feeds(url: str) -> t.Collection[dict[str, str]]:
    """
    Discover any feeds at the given URL.

    Args:
        url: URL of page to extract feeds from.

    Returns:
        The feeds in order of priority. Atom feeds are prioritised first, followed by RDF, and then finally RSS feeds.
    """
    links, _ = discovery.fetch_meta(url, _FeedExtractor)
    return sorted(links, key=(lambda feed: _ORDER[feed["type"]]))
