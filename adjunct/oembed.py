"""
An oEmbed_ client library.

.. _oEmbed: http://oembed.com/
"""

import json
from urllib import parse, request
import xml.sax
import xml.sax.handler

from adjunct import discovery


__all__ = ["get_oembed"]


# pylint: disable-msg=C0103
class OEmbedContentHandler(xml.sax.handler.ContentHandler):
    """
    Pulls the fields out of an XML oEmbed document.
    """

    valid_fields = [
        "type",
        "version",
        "title",
        "cache_age",
        "author_name",
        "author_url",
        "provider_name",
        "provider_url",
        "thumbnail_url",
        "thumbnail_width",
        "thumbnail_height",
    ]

    def __init__(self):
        super().__init__()
        self.current_field = None
        self.current_value = None
        self.depth = 0
        self.fields = {}

    def startElement(self, name, attrs):
        self.depth += 1
        if self.depth == 2:
            self.current_field = name
            self.current_value = ""

    def endElement(self, name):
        if self.depth == 2 and self.current_field in self.valid_fields:
            self.fields[self.current_field] = self.current_value
        self.depth -= 1

    def characters(self, content):
        if self.depth == 2:
            self.current_value += content


def fetch_oembed_document(url, max_width=None, max_height=None):
    """
    Fetch the oEmbed document for a resource at `url` from the provider. If you
    want to constrain the dimensions of the thumbnail, specify the maximum
    width in `max_width` and the maximum height in `max_height`.
    """
    # Append on the height and width parameters if needed.
    additional = {}
    for key, value in (("maxwidth", max_width), ("maxheight", max_height)):
        if value is not None:
            additional[key] = value
    if len(additional) > 0:
        url = "%s&%s" % (url, parse.urlencode(additional))

    req = request.Request(
        url, headers={"Accept": ", ".join(list(ACCEPTABLE_TYPES.keys()))}
    )
    with request.urlopen(req) as fh:
        info = fh.info()
        content_type = info.get("content-type", None)
        if content_type in ACCEPTABLE_TYPES:
            parser = ACCEPTABLE_TYPES[content_type]
            return parser(fh)
    return None


def parse_xml_oembed_response(fh):
    """
    Parse the fields from an XML OEmbed document.
    """
    handler = OEmbedContentHandler()
    xml.sax.parse(fh, handler)
    return handler.fields


# Types we'll accept and their parsers. I think it's a design flaw of oEmbed
# that (a) these content types aren't the same as the link types and (b) that
# text/xml (which is deprecated, IIRC) is being used rather than
# application/xml. Just to be perverse, let's support all of that.
ACCEPTABLE_TYPES = {
    "application/json": json.load,
    "application/json+oembed": json.load,
    "application/xml": parse_xml_oembed_response,
    "application/xml+oembed": parse_xml_oembed_response,
    "text/xml": parse_xml_oembed_response,
    "text/xml+oembed": parse_xml_oembed_response,
}

LINK_TYPES = [key for key in ACCEPTABLE_TYPES if key.endswith("+oembed")]


def find_first_oembed_link(links):
    """
    Search for the first valid oEmbed link.
    """
    for link in links:
        # For safety's sake.
        if "rel" not in link or "type" not in link or "href" not in link:
            continue
        if link["rel"] == "alternate" and link["type"] in LINK_TYPES:
            return link["href"]
    return None


def get_oembed(url, max_width=None, max_height=None):
    """
    Given a URL, fetch its associated oEmbed information.
    """
    oembed_url = find_first_oembed_link(discovery.fetch_links(url))
    if oembed_url is None:
        return None
    return fetch_oembed_document(oembed_url, max_width, max_height)
