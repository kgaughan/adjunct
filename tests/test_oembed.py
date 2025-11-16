import io
import json
import unittest
from unittest import mock
from urllib import error

import pytest

from adjunct import fixtureutils
from adjunct.fixtureutils import make_fake_http_response
from adjunct.oembed import (
    _build_url,
    _parse_xml_oembed_response,
    fetch_oembed_document,
    find_first_oembed_link,
)


class BuildUrlTest(unittest.TestCase):
    def test_base(self):
        self.assertEqual(_build_url("foo", None, None), "foo")

    def test_dimension(self):
        self.assertEqual(_build_url("foo", 5, None), "foo&maxwidth=5")
        self.assertEqual(_build_url("foo", None, 8), "foo&maxheight=8")
        self.assertEqual(_build_url("foo", 5, 8), "foo&maxwidth=5&maxheight=8")


LINKS_WITHOUT = [
    {"href": "https://www.example.com/style.css", "rel": "stylesheet"},
    {"href": "https://www.example.com/", "rel": "canonical"},
    {"href": "https://m.example.com/", "media": "handheld", "rel": "alternate"},
    {"href": "https://cdn.example.com/favicon.png", "rel": "icon"},
]


class OEmbedFinderTest(unittest.TestCase):
    def test_none(self):
        self.assertIsNone(find_first_oembed_link(LINKS_WITHOUT))

    def test_find(self):
        links = [
            *LINKS_WITHOUT,
            {
                "href": "http://www.example.com/oembed?format=json",
                "rel": "alternate",
                "title": "JSON Example",
                "type": "application/json+oembed",
            },
            {
                "href": "http://www.example.com/oembed?format=xml",
                "rel": "alternate",
                "title": "XML Example",
                "type": "text/xml+oembed",
            },
        ]
        result = find_first_oembed_link(links)
        self.assertEqual(result, "http://www.example.com/oembed?format=json")

    def test_no_href(self):
        links = [
            *LINKS_WITHOUT,
            {
                "rel": "alternate",
                "title": "JSON Example",
                "type": "application/json+oembed",
            },
            {
                "href": "http://www.example.com/oembed?format=xml",
                "rel": "alternate",
                "title": "XML Example",
                "type": "text/xml+oembed",
            },
        ]
        result = find_first_oembed_link(links)
        self.assertEqual(result, "http://www.example.com/oembed?format=xml")


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
        fields = _parse_xml_oembed_response(fh)
        self.assertDictEqual(
            fields,
            {
                "version": "1.0",
                "type": "photo",
                "title": "This is a title",
                "width": "300",
                "height": "300",
            },
        )


def make_response(dct, content_type="application/json+oembed; charset=UTF-8"):
    return make_fake_http_response(
        body=json.dumps(dct),
        headers={"Content-Type": content_type},
    )


class FetchTest(unittest.TestCase):
    @mock.patch("urllib.request.urlopen")
    def test_fetch(self, mock_urlopen):
        orig = {
            "version": "1.0",
            "type": "video",
            "html": "<video/>",
            "width": 480,
            "height": 270,
            "author_name": "John Doe",
            "title": "A video",
        }
        mock_urlopen.return_value = make_response(orig)

        fetched = fetch_oembed_document("https://example.com/oembed?type=json")
        mock_urlopen.assert_called_once()
        self.assertIsInstance(fetched, dict)
        self.assertDictEqual(fetched, orig)  # type: ignore

    @mock.patch("urllib.request.urlopen")
    def test_fetch_bad(self, mock_urlopen):
        mock_urlopen.return_value = make_response({}, content_type="text/plain")

        fetched = fetch_oembed_document("https://example.com/oembed?type=json")
        mock_urlopen.assert_called_once()
        self.assertIsNone(fetched)


def app_400(environ, start_response):  # noqa: ARG001
    headers = [("Content-Type", "text/plain; charset=utf-8")]
    start_response("400 Bad Request", headers)
    return [b"Bad request"]


def app_500(environ, start_response):  # noqa: ARG001
    headers = [("Content-Type", "text/plain; charset=utf-8")]
    start_response("500 Internal Server Error", headers)
    return [b"Internal server error"]


def test_fetch_oembed_with_error():
    with fixtureutils.fixture(app_400) as addr:
        fetched = fetch_oembed_document(f"{addr}/oembed")
        assert fetched is None

    with fixtureutils.fixture(app_500) as addr, pytest.raises(error.HTTPError):
        fetch_oembed_document(f"{addr}/oembed")
