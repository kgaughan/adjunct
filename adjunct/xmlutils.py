"""
XML utilities.
"""

import contextlib
from xml.sax import saxutils
try:
    import cStringIO as stringio
except ImportError:
    import StringIO as stringio


class XMLBuilder(object):
    """
    Generates an XML document.
    """

    def __init__(self, out=None, encoding='utf-8'):
        """
        `out` should be a file-like object to write the document to. If none
        is provided, a buffer is created.
        """
        if out is None:
            self.buffer = stringio.StringIO()
            out = self.buffer
        else:
            self.buffer = None
        self.generator = saxutils.XMLGenerator(out, encoding)
        self.generator.startDocument()

    @contextlib.contextmanager
    def within(self, tag, **attrs):
        """
        Generates an element containing nested elements.
        """
        self.generator.startElement(tag, attrs)
        yield
        self.generator.endElement(tag)

    def tag(self, tag, *values, **attrs):
        """
        Generates a simple element.
        """
        self.generator.startElement(tag, attrs)
        for value in values:
            self.generator.characters(value)
        self.generator.endElement(tag)
        return self

    def append(self, other):
        """
        Append the string to this document.
        """
        self.generator.characters(other)
        return self

    def as_string(self):
        """
        If using the built-in buffer, get its current contents.
        """
        if self.buffer is None:
            return None
        return self.buffer.getvalue()

    def close(self):
        """
        If using the built-in buffer, clean it up.
        """
        if self.buffer is not None:
            self.buffer.close()
            self.buffer = None

    # Shortcuts.
    __iadd__ = append
    __str__ = as_string
