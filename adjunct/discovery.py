"""
Discovery via HTML <link> elements.
"""


import contextlib
import HTMLParser
import urllib2


__all__ = (
    'fetch_links',
)


# pylint: disable-msg=R0904
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
        """
        Extract the link tags from header of a HTML document to be read from
        the file object, `fh`. The return value is a list of dicts where the
        values of each are the attributes of the link elements encountered.
        """
        parser = LinkExtractor()
        with contextlib.closing(parser):
            while not parser.finished:
                chunk = fh.read(2048)
                if chunk == '':
                    break
                parser.feed(chunk)
        return parser.collected


def fetch_links(url):
    """
    Extract the <link> tags from the HTML document at the given URL.
    """
    fh = urllib2.urlopen(url)
    with contextlib.closing(fh):
        return LinkExtractor.extract(fh)
