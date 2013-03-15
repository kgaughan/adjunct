"""
An oEmbed_ client library.

.. _oEmbed: http://oembed.com/

Copyright (c) Keith Gaughan, 2013.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import contextlib
import json
import urllib
import urllib2
import xml.sax
import xml.sax.handler

from adjunct import discovery


__all__ = (
    'get_oembed',
)

__version__ = '0.1.0'
__author__ = 'Keith Gaughan'
__email__ = 'k@stereochro.me'


# pylint: disable-msg=C0103
class OEmbedContentHandler(xml.sax.handler.ContentHandler):
    """
    Pulls the fields out of an XML oEmbed document.
    """

    valid_fields = set([
        'type', 'version', 'title', 'cache_age',
        'author_name', 'author_url',
        'provider_name', 'provider_url',
        'thumbnail_url', 'thumbnail_width', 'thumbnail_height',
    ])

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
    oembed_url = find_first_oembed_link(discovery.fetch_links(url))
    if oembed_url is None:
        return None
    return fetch_oembed_document(oembed_url, max_width, max_height)
