import io
import unittest

from adjunct.discovery import Extractor


class ExtractorTest(unittest.TestCase):
    def test_empty(self):
        buf = io.BytesIO(
            b"""<!DOCTYPE html>
<html></html>"""
        )
        self.assertListEqual(Extractor.extract(buf).collected, [])

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
            Extractor.extract(buf).collected, [{"href": "bar", "rel": "foo"}],
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
            Extractor.extract(buf).collected,
            [{"href": "http://example.com/bar", "rel": "foo"}],
        )
