import io
import unittest

from adjunct.oembed import parse_xml_oembed_response


class OEmbedXMLParserTest(unittest.TestCase):

    def test_parse(self):
        fh = io.StringIO(
            """<?xml version="1.0" encoding="utf-8"?>
<oembed>
    <version>1.0</version>
    <type>photo</type>
    <title>This is a title</title>
    <url>http://example.com/foo.png</url>
    <height>300</height>
    <width>300</width>
</oembed>
"""
        )
        fields = parse_xml_oembed_response(fh)
        self.assertDictEqual(
            fields, {"version": "1.0", "type": "photo", "title": "This is a title"}
        )
