"""A simple, nay, simplistic! [OPML] parser.

[OPML]: http://dev.opml.org/spec2.html
"""

import datetime as dt
import email.utils
import typing as t
import xml.sax
import xml.sax.handler

__all__ = [
    "OpmlError",
    "Outline",
    "parse",
    "parse_string",
    "parse_timestamp",
]


class OpmlError(Exception):
    """Raised when there's a problem parsing an OPML document."""


class Outline(list):
    """An outline.

    Contains the element's attributes in the `attrs` member and the outlines
    nested within it as elements.

    Args:
        attrs: any attributes on the element
        items: any child outlines nested within this outline
        root: is this outline the root outline?

    Attributes:
        attrs: any attributes on the element
        root: is this outline the root outline?

    """

    def __init__(
        self,
        attrs: dict[str, str] | None = None,
        items: t.Sequence["Outline"] = (),
        *,
        root: bool = False,
    ) -> None:
        super().__init__()
        self.attrs: dict[str, str] = {} if attrs is None else attrs
        self.root: bool = root
        self.extend(items)

    def __repr__(self) -> str:
        args = []
        if self.root:
            args.append("root=True")
        if len(self.attrs) > 0:
            args.append(f"attrs={self.attrs!r}")
        if len(self) > 0:
            args.append(f"items={list(self)!r}")
        return f"Outline({', '.join(args)})"


class _Handler(xml.sax.handler.ContentHandler):
    """Implements the mechanics of parsing an OPML document."""

    _HEAD_TAGS = [  # noqa: RUF012
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
    _NESTING = {  # noqa: RUF012
        None: ["opml"],
        "opml": ["head", "body"],
        "head": _HEAD_TAGS,
        "body": ["outline"],
        "outline": ["outline"],
    }

    def __init__(self) -> None:
        super().__init__()
        self.tag_stack: list[str] = []
        self.outline_stack: list[Outline] = []
        self.root: Outline | None = None

    def _get_parent_tag(self) -> str | None:
        """Oh, guess!"""
        return None if len(self.tag_stack) == 0 else self.tag_stack[-1]

    def startDocument(self) -> None:  # noqa: N802
        self.root = Outline(root=True)
        self.outline_stack = [self.root]
        self.tag_stack = []

    def startElement(self, name, attrs) -> None:  # noqa: N802
        expected = self._NESTING[self._get_parent_tag()]
        if name not in expected:
            raise OpmlError(f"Got <{name}>, expected <{'|'.join(expected)}>")

        self.tag_stack.append(name)
        if name == "outline":
            outline = Outline()
            self.outline_stack[-1].append(outline)
            self.outline_stack.append(outline)
            outline.attrs = dict(attrs.items())
            for attr in ("isComment", "isBreakpoint"):
                outline.attrs.setdefault(attr, "false")

    def endElement(self, name) -> None:  # noqa: N802
        self.tag_stack.pop()
        if name == "outline":
            self.outline_stack.pop()

    def characters(self, content) -> None:
        content = content.strip()
        parent = self._get_parent_tag()
        if content != "" and parent in self._HEAD_TAGS and self.root is not None:
            self.root.attrs[parent] = content


def parse_timestamp(ts: str) -> dt.datetime | None:
    """Convert an RFC 2822 timestamp (as used in OPML) to a UTC DateTime object.

    Args:
        ts: an RFC 2822 timestamp

    Returns:
        A timezone-aware datetime, or `None` if the timestamp could not be parsed.

    """
    tt = email.utils.parsedate_tz(ts)
    if tt is None:
        return None
    return dt.datetime.fromtimestamp(email.utils.mktime_tz(tt), tz=dt.UTC)


def parse(fh: t.TextIO) -> Outline | None:
    """Parse an OPML file from the given file object.

    Args:
        fh: a file-like object containing an OPML document

    Returns:
        An outline if the document could be parsed, otherwise `None`.

    """
    handler = _Handler()
    xml.sax.parse(fh, handler)
    return handler.root


def parse_string(s: str) -> Outline | None:
    """Parse an OPML document from the given string.

    Args:
        s: an OPML document.

    Returns:
        An outline if the document could be parsed, otherwise `None`.

    """
    handler = _Handler()
    xml.sax.parseString(s, handler)
    return handler.root
