import os.path
import unittest

from adjunct import discovery, ogp

HERE = os.path.dirname(__file__)


class TestOPG(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        with open(os.path.join(HERE, "ogp.html"), "rb") as fh:
            self.raw_properties = discovery.Extractor.extract(fh).properties
        self.properties = ogp.parse(self.raw_properties)

    def test_size(self):
        self.assertEqual(len(self.raw_properties), 11)
        self.assertEqual(len(self.properties), 7)

    def test_access(self):
        self.assertEqual(len(list(ogp.find(self.properties, "type", "song"))), 1)

    def test_invalid(self):
        self.assertEqual(len(list(ogp.find(self.properties, "audio"))), 0)

    def test_video(self):
        videos = list(ogp.find(self.properties, "video"))
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0].value, videos[0].metadata["secure_url"])
        self.assertSetEqual(
            set(videos[0].metadata.keys()),
            {"secure_url", "type", "width", "height"},
        )

    def test_meta(self):
        meta = ogp.to_meta(self.properties)
        with open(os.path.join(HERE, "ogp-minotaur-shock.html")) as fh:
            expected = fh.read().strip()
        self.assertEqual(meta, expected)
