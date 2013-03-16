"""
Discovery via HTML <link> elements.
"""


import contextlib
import HTMLParser
import urllib2
import urlparse


__all__ = (
    'fetch_links',
)


# pylint: disable-msg=R0904
class LinkExtractor(HTMLParser.HTMLParser):
    """
    A simple subclass of `HTMLParser` for extracting <link> tags from the
    header of a HTML document.
    """

    def __init__(self, base):
        HTMLParser.HTMLParser.__init__(self)
        self.active = False
        self.finished = False
        self.base = base
        self.collected = []

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.active = True
        elif self.active:
            if tag == 'link':
                self.collected.append(dict(attrs))
            elif tag == 'base' and 'href' in attrs:
                self.base = urlparse.urljoin(self.base, attrs['href'])

    def handle_endtag(self, tag):
        if tag == 'head':
            self.active = False
            self.finished = True

    @staticmethod
    def extract(fh, base='.'):
        """
        Extract the link tags from header of a HTML document to be read from
        the file object, `fh`. The return value is a list of dicts where the
        values of each are the attributes of the link elements encountered.
        """
        parser = LinkExtractor(base)
        with contextlib.closing(parser):
            while not parser.finished:
                chunk = fh.read(2048)
                if chunk == '':
                    break
                parser.feed(chunk)

        # Canonicalise the URL paths.
        for link in parser.collected:
            if 'href' in link:
                link['href'] = urlparse.urljoin(parser.base, link['href'])

        return parser.collected


def fetch_links(url):
    """
    Extract the <link> tags from the HTML document at the given URL.
    """
    fh = urllib2.urlopen(url)
    with contextlib.closing(fh):
        return LinkExtractor.extract(fh, url)
