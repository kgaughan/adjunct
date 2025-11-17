import io
import unittest

from adjunct import discovery, fixtureutils


class ExtractorTest(unittest.TestCase):
    def test_empty(self):
        buf = io.BytesIO(
            b"""<!DOCTYPE html>
<html></html>"""
        )
        self.assertListEqual(discovery.Extractor.extract(buf).collected, [])

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
            discovery.Extractor.extract(buf).collected,
            [{"href": "bar", "rel": "foo"}],
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
            discovery.Extractor.extract(buf).collected,
            [{"href": "http://example.com/bar", "rel": "foo"}],
        )


def meta_app(environ, start_response):  # noqa: ARG001
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Link", "http://malformed.example.com/"),
        ("Link", '<http://example.com/>; rel="bar"'),
    ]
    start_response("200 OK", headers)
    return [
        b"""<!DOCTYPE html>
<html>
    <head>
        <link rel="foo" href="bar">
        <meta property="og:title" content="Example">
    </head>
</html>"""
    ]


def test_fetch_meta():
    with fixtureutils.fixture(meta_app) as addr:
        links, properties = discovery.fetch_meta(addr)
        assert links == [
            {"href": "http://example.com/", "rel": "bar"},
            {"href": f"{addr}bar", "rel": "foo"},
        ]
        assert properties == [("og:title", "Example")]


def test_safe_slurp():
    data = b"Hello, world!\nThis is a test.\n"
    fh = io.BytesIO(data)
    result = "".join(discovery._safe_slurp(fh, chunk_size=4, encoding="utf-8"))
    assert result == data.decode("utf-8")


def test_fix_attributes():
    assert discovery._fix_attributes(
        [
            ("REL", " Foo "),
            ("data-value", None),
            ("Type", "TEXT/HTML"),
            ("TITLE", "Preserve Case"),
        ]
    ) == {
        "rel": "foo",
        "data-value": "",
        "type": "text/html",
        "title": "Preserve Case",
    }
