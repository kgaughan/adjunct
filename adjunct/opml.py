"""
A simple, nay, simplistic! OPML_ parser.

.. _OPML: http://dev.opml.org/spec2.html
"""

import xml.sax
import xml.sax.handler


__all__ = (
    'Outline',
    'parse', 'parse_string',
)


class Outline(list):
    """
    An outline. Contains the element's attributes in the `attrs` member and
    the outlines nested within it as elements.
    """

    def __init__(self, *args, **kwargs):
        super(Outline, self).__init__(*args, **kwargs)
        self.attrs = {}

    def __repr__(self):
        if len(self) > 0:
            return '<Outline %r %r>' % (self.attrs, list(self))
        return '<Outline %r>' % (self.attrs,)


class _Handler(xml.sax.handler.ContentHandler):
    """
    Implements the mechanics of parsing an OPML document.
    """

    meta_tags = [
        'title',
        'dateCreated',
        'dateModified',
        'ownerName',
        'ownerEmail',
        'ownerId',
        'docs',
        'expansionState',
        'vertScrollState',
        'windowTop',
        'windowLeft',
        'windowBottom',
        'windowRight',
    ]

    # Some simplistic validation: ensure that the elements in the document
    # are nested as we'd expect.
    nesting = {
        None: ['opml'],
        'opml': ['head', 'body'],
        'head': meta_tags,
        'body': ['outline'],
        'outline': ['outline'],
    }

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.tag_stack = []
        self.outline_stack = []
        self.root = None
        self.current = None

    def _get_parent_tag(self):
        """
        Oh, guess!
        """
        return None if len(self.tag_stack) == 0 else self.tag_stack[-1]

    def startDocument(self):  # pylint: disable=C0103
        self.root = Outline()
        self.outline_stack = [self.root]
        self.tag_stack = []

    def endDocument(self):  # pylint: disable=C0103
        self.current = None

    def startElement(self, tag, attrs):  # pylint: disable=C0103
        if tag not in self.nesting[self._get_parent_tag()]:
            raise Exception('WAT')
        self.tag_stack.append(tag)
        if tag == 'outline':
            outline = Outline()
            self.outline_stack[-1].append(outline)
            self.outline_stack.append(outline)
            outline.attrs = dict(
                (name, attrs.getValue(name))
                for name in attrs.getNames())

    def endElement(self, tag):  # pylint: disable=C0103
        self.tag_stack.pop()
        if tag == 'outline':
            self.outline_stack.pop()

    def characters(self, content):
        content = content.strip()
        parent = self._get_parent_tag()
        if content != '' and parent in self.meta_tags:
            self.root.attrs[parent] = content


def parse(fh):
    """
    Parses an OPML file from the given file object.
    """
    handler = _Handler()
    xml.sax.parse(fh, handler)
    return handler.root


def parse_string(s):
    """
    Parses an OPML document from the given string.
    """
    handler = _Handler()
    xml.sax.parseString(s, handler)
    return handler.root
