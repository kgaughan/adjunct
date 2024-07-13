import io
import unittest

from adjunct.xmlutils import XMLBuilder


class XMLBuilderTest(unittest.TestCase):
    def test_basics(self):
        xml = XMLBuilder()
        self.assertIsNotNone(xml.buffer)
        with xml.within("root", xmlns="tag:talideon.com,2013:test"):
            xml += "Before"
            with xml.within("leaf"):
                xml += "Within"
            xml += "After"
            xml.tag("leaf", "Another")
        self.assertEqual(
            xml.as_string(),
            """<?xml version="1.0" encoding="utf-8"?>
<root xmlns="tag:talideon.com,2013:test">Before<leaf>Within</leaf>After<leaf>Another</leaf></root>""",
        )
        xml.close()
        self.assertIsNone(xml.buffer)

    def test_own_buffer(self):
        buf = io.StringIO()
        xml = XMLBuilder(buf)
        self.assertIsNone(xml.buffer)
        with xml.within("root", xmlns="myns"):
            xml += "Body"
        self.assertEqual(xml.as_string(), "")
        self.assertEqual(
            buf.getvalue(),
            """<?xml version="1.0" encoding="utf-8"?>
<root xmlns="myns">Body</root>""",
        )
        xml.close()

    def test_attrs(self):
        xml = XMLBuilder()
        xml.root(xmlns="myns")
        self.assertEqual(
            xml.as_string(),
            """<?xml version="1.0" encoding="utf-8"?>
<root xmlns="myns"></root>""",
        )
        xml.close()
