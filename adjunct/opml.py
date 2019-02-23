"""
A simple, nay, simplistic! OPML_ parser.

.. _OPML: http://dev.opml.org/spec2.html
"""

import datetime
import email.utils
import xml.sax
import xml.sax.handler


__all__ = ["Outline", "OpmlError", "parse", "parse_string", "parse_timestamp"]


class OpmlError(Exception):
    """
    Raised when there's a problem parsing an OPML document.
    """


class Outline(list):
    """
    An outline. Contains the element's attributes in the `attrs` member and
    the outlines nested within it as elements.
    """

    def __init__(self, attrs=None, items=(), root=False):
        super().__init__()
        self.attrs = {} if attrs is None else attrs
        self.root = root
        self.extend(items)

    def __repr__(self):
        args = []
        if self.root:
            args.append("root=True")
        if len(self.attrs) > 0:
            args.append("attrs=%r" % self.attrs)
        if len(self) > 0:
            args.append("items=%r" % list(self))
        return "Outline(%s)" % ", ".join(args)


class _Handler(xml.sax.handler.ContentHandler):
    """
    Implements the mechanics of parsing an OPML document.
    """

    head_tags = [
        "title",
        "dateCreated",
        "dateModified",
        "ownerName",
        "ownerEmail",
        "ownerId",
        "docs",
        "expansionState",
        "vertScrollState",
        "windowTop",
        "windowLeft",
        "windowBottom",
        "windowRight",
    ]

    # Some simplistic validation: ensure that the elements in the document
    # are nested as we'd expect.
    nesting = {
        None: ["opml"],
        "opml": ["head", "body"],
        "head": head_tags,
        "body": ["outline"],
        "outline": ["outline"],
    }

    def __init__(self):
        super().__init__(self)
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
        self.root = Outline(root=True)
        self.outline_stack = [self.root]
        self.tag_stack = []

    def endDocument(self):  # pylint: disable=C0103
        self.current = None

    def startElement(self, tag, attrs):  # pylint: disable=C0103
        expected = self.nesting[self._get_parent_tag()]
        if tag not in expected:
            raise OpmlError("Got <%s>, expected <%s>" % (tag, "|".join(expected)))

        self.tag_stack.append(tag)
        if tag == "outline":
            outline = Outline()
            self.outline_stack[-1].append(outline)
            self.outline_stack.append(outline)
            outline.attrs = dict(attrs.items())
            for attr in ("isComment", "isBreakpoint"):
                outline.attrs.setdefault(attr, "false")

    def endElement(self, tag):  # pylint: disable=C0103
        self.tag_stack.pop()
        if tag == "outline":
            self.outline_stack.pop()

    def characters(self, content):
        content = content.strip()
        parent = self._get_parent_tag()
        if content != "" and parent in self.head_tags:
            self.root.attrs[parent] = content


def parse_timestamp(ts):
    """
    Convert an RFC 2822 timestamp (as used in OPML) to a UTC DateTime object.
    """
    return datetime.datetime.utcfromtimestamp(
        email.utils.mktime_tz(email.utils.parsedate_tz(ts))
    )


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
