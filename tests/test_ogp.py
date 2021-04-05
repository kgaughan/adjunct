import os.path
import unittest

from adjunct import discovery, ogp

HERE = os.path.dirname(__file__)


class OPGTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(HERE, "ogp.html"), "rb") as fh:
            self.properties = discovery.Extractor.extract(fh).properties
        self.root = ogp.Root()
        for prop, content in self.properties:
            self.root.insert(prop, content)

    def test_size(self):
        self.assertEqual(len(self.properties), 16)
        self.assertEqual(len(self.properties), len(list(self.root.flatten())))

    def test_access(self):
        self.assertSetEqual(set(self.root.attrs.keys()), {"og", "twitter"})
        self.assertEqual(str(self.root.get("og:type")), "song")

    def test_invalid(self):
        elem = self.root.get("og:audio")
        self.assertEqual(len(elem), 1)
        # Ensure this doesn't add anything
        self.assertEqual(len(self.properties), len(list(self.root.flatten())))
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

    def test_meta(self):
        meta = str(self.root)
        expected = """
<meta property="og:title" content="Ocean Swell, by Minotaur Shock">
<meta property="og:type" content="song">
<meta property="og:site_name" content="Minotaur Shock">
<meta property="og:description" content="from the album Orchard">
<meta property="og:image" content="https://f4.bcbits.com/img/a3081644212_5.jpg">
<meta property="og:url" content="https://minotaurshock.bandcamp.com/track/ocean-swell">
<meta property="og:video" content="https://bandcamp.com/EmbeddedPlayer/v=2/track=1335882601/size=large/tracklist=false/artwork=small/">
<meta property="og:video:secure_url" content="https://bandcamp.com/EmbeddedPlayer/v=2/track=1335882601/size=large/tracklist=false/artwork=small/">
<meta property="og:video:type" content="text/html">
<meta property="og:video:height" content="120">
<meta property="og:video:width" content="400">
<meta property="twitter:site" content="@bandcamp">
<meta property="twitter:card" content="player">
<meta property="twitter:player" content="https://bandcamp.com/EmbeddedPlayer/v=2/track=1335882601/size=large/linkcol=0084B4/notracklist=true/twittercard=true/">
<meta property="twitter:player:height" content="467">
<meta property="twitter:player:width" content="350">
"""
        self.assertEqual(meta.strip(), expected.strip())
