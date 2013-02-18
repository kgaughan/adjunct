"""
An oEmbed_ client library.

.. _oEmbed: http://oembed.com/
"""

import contextlib
import HTMLParser
import json
import urllib
import urllib2
import xml.sax
import xml.sax.handler


__all__ = (
    'get_oembed',
)


class LinkExtractor(HTMLParser.HTMLParser):
    """
    A simple subclass of `HTMLParser` for extracting <link> tags from the
    header of a HTML document.
    """

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.active = False
        self.finished = False
        self.collected = []

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.active = True
        elif self.active and tag == 'link':
            self.collected.append(dict(attrs))

    def handle_endtag(self, tag):
        if tag == 'head':
            self.active = False
            self.finished = True

    @staticmethod
    def extract(fh):
        parser = LinkExtractor()
        with contextlib.closing(parser):
            while not parser.finished:
                chunk = fh.read(2048)
                if chunk == '':
                    break
                parser.feed(chunk)
        return parser.collected


class OEmbedContentHandler(xml.sax.handler.ContentHandler):
    """
    Pulls the fields out of an XML oEmbed document.
    """

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.current_field = None
        self.current_value = None
        self.depth = 0
        self.fields = {}

    def startElement(self, name, attrs):
        self.depth += 1
        if self.depth == 2:
            self.current_field = name
            self.current_value = ''

    def endElement(self, name):
        if self.depth == 2:
            self.fields[self.current_field] = self.current_value
        self.depth -= 1

    def characters(self, content):
        if self.depth == 2:
            self.current_value += content


def fetch_links(url):
    """
    Extract the <link> tags from the HTML document at the given URL.
    """
    fh = urllib2.urlopen(url)
    with contextlib.closing(fh):
        return LinkExtractor.extract(fh)


def fetch_oembed_document(url, max_width=None, max_height=None):
    # Append on the height and width parameters if needed.
    additional = {}
    for key, value in (('maxwidth', max_width), ('maxheight', max_height)):
        if value is not None:
            additional[key] = value
    if len(additional) > 0:
        url = "%s&%s" % (url, urllib.urlencode(additional))

    request = urllib2.Request(
        url, headers={'Accept': ', '.join(ACCEPTABLE_TYPES.keys())})
    fh = urllib2.urlopen(request)
    with contextlib.closing(fh):
        info = fh.info()
        content_type = info.get('content-type', None)
        if content_type in ACCEPTABLE_TYPES:
            parser = ACCEPTABLE_TYPES[content_type]
            return parser(fh)
    return None


def parse_xml_oembed_response(fh):
    handler = OEmbedContentHandler()
    xml.sax.parse(fh, handler)
    return handler.fields


# Types we'll accept and their parsers. I think it's a design flaw of oEmbed
# that (a) these content types aren't the same as the link types and (b) that
# text/xml (which is deprecated, IIRC) is being used rather than
# application/xml. Just to be perverse, let's support all of that.
ACCEPTABLE_TYPES = {
    'application/json': json.load,
    'application/json+oembed': json.load,
    'application/xml': parse_xml_oembed_response,
    'application/xml+oembed': parse_xml_oembed_response,
    'text/xml': parse_xml_oembed_response,
    'text/xml+oembed': parse_xml_oembed_response,
}

LINK_TYPES = [key for key in ACCEPTABLE_TYPES if key.endswith('+oembed')]


def find_first_oembed_link(links):
    """
    Search for the first valid oEmbed link.
    """
    for link in links:
        # For safety's sake.
        if 'rel' not in link or 'type' not in link or 'href' not in link:
            continue
        if link['rel'] == 'alternate' and link['type'] in LINK_TYPES:
            return link['href']
    return None


def get_oembed(url, max_width=None, max_height=None):
    """
    Given a URL, fetch its associated oEmbed information.
    """
    oembed_url = find_first_oembed_link(fetch_links(url))
    if oembed_url is None:
        return None
    return fetch_oembed_document(oembed_url, max_width, max_height)
