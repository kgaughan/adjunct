import io
import unittest

from adjunct.discovery import LinkExtractor


class LinkExtractorTest(unittest.TestCase):
    def test_empty(self):
        buf = io.BytesIO(
            b"""<!DOCTYPE html>
<html></html>"""
        )
        self.assertListEqual(LinkExtractor.extract(buf), [])

    def test_one_link(self):
        buf = io.BytesIO(
            b"""<!DOCTYPE html>
<html>
    <head>
        <link rel="foo" href="bar">
    </head>
</html>"""
        )
        self.assertListEqual(
            LinkExtractor.extract(buf), [{"href": "bar", "rel": "foo"}],
        )

    def test_one_link_with_base(self):
        buf = io.BytesIO(
            b"""<!DOCTYPE html>
<html>
    <head>
        <link rel="foo" href="bar">
        <base href="http://example.com/">
    </head>
</html>"""
        )
        self.assertListEqual(
            LinkExtractor.extract(buf),
            [{"href": "http://example.com/bar", "rel": "foo"}],
        )
