import os.path
import unittest

from adjunct import discovery, ogp

HERE = os.path.dirname(__file__)


def load_fixture(name: str) -> str:
    with open(os.path.join(HERE, name), "r") as fh:
        return fh.read().strip()


class TestOPG(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        with open(os.path.join(HERE, "ogp.html"), "rb") as fh:
            self.properties = discovery.Extractor.extract(fh).properties
        self.root = ogp.parse(self.properties)

    def test_size(self):
        self.assertEqual(len(self.properties), 11)

    """
    def test_access(self):
        self.assertSetEqual(set(self.root.attrs.keys()), {"og", "twitter"})
        self.assertEqual(str(self.root.get("og:type")), "song")

    def test_invalid(self):
        elem = self.root.get("og:audio")
        self.assertEqual(len(elem), 1)
        self.assertIsInstance(elem, ogp.SingleValue)
        self.assertIsNone(elem.content)
        self.assertDictEqual(elem.attrs, {})

    def test_video(self):
        videos = list(self.root.get_all("og:video"))
        self.assertEqual(len(videos), 1)
        attrs = dict(videos[0].flatten())
        self.assertEqual(videos[0].content, attrs["secure_url"])
        self.assertSetEqual(
            set(attrs.keys()),
            {"secure_url", "type", "width", "height"},
        )
    """

    def test_meta(self):
        meta = ogp.to_meta(self.root)
        expected = load_fixture("ogp-minotaur-shock.html")
        self.assertEqual(meta, expected)


class TestMultiValue(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        properties = [
            ("og:title", "Testing"),
            ("og:title", "Testing Again"),
            ("og:video", "http://example.com/video1.mpg"),
            ("og:video:height", "52"),
            ("og:video:width", "25"),
            ("og:video", "http://example.com/video2.mpg"),
            ("og:video:height", "64"),
            ("og:video:width", "46"),
        ]
        self.root = ogp.parse(properties)

    """
    def test_multivalue(self):
        items = list(self.root.get_all("og:title"))
        self.assertEqual(len(items), 2)
        self.assertListEqual(
            [str(item) for item in items],
            ["Testing", "Testing Again"],
        )
    """

    def test_flatten(self):
        meta = ogp.to_meta(self.root)
        expected = load_fixture("ogp-flatten.html")
        self.assertEqual(meta, expected)
