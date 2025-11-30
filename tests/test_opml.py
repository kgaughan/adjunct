import datetime
import os.path
import unittest

from adjunct import opml

HERE = os.path.dirname(__file__)


class OPMLTest(unittest.TestCase):
    def test_parse_file(self):
        with open(os.path.join(HERE, "sample.opml")) as fh:
            doc = opml.parse(fh)

        assert doc is not None
        self.assertTrue(doc.root)
        self.assertEqual(len(doc.attrs), 1)
        self.assertEqual(doc.attrs["title"], "Sample OPML file")
        self.assertEqual(len(doc), 3)

        # Check the top-level categories.
        self.assertEqual(len(doc[0]), 2)
        self.assertEqual(len(doc[1]), 1)
        self.assertEqual(len(doc[2]), 1)

        # Check the last category and the one feed within it.
        self.assertEqual(doc[2].attrs["text"], "Personal")
        cant_hack = doc[2][0]
        # 5, because it includes isComment and isBreakpoint implicitly
        self.assertEqual(len(cant_hack.attrs), 5)
        self.assertEqual(len(cant_hack), 0)
        self.assertEqual(cant_hack.attrs["text"], "Can't Hack")
        self.assertEqual(cant_hack.attrs["type"], "rss")
        self.assertEqual(cant_hack.attrs["xmlUrl"], "https://i.canthack.it/feeds/all.xml")
        self.assertEqual(cant_hack.attrs["isComment"], "false")
        self.assertEqual(cant_hack.attrs["isBreakpoint"], "false")

    def test_exception(self):
        with self.assertRaises(opml.OpmlError):
            opml.parse_string('<?xml version="1.0" encoding="UTF-8"?><opml version="1.0"><outline/></opml>')

    def test_date_parse(self):
        # Note: the resulting date is in UTC.
        self.assertEqual(
            opml.parse_timestamp("Fri, 21 Nov 1997 09:55:06 -0600"),
            datetime.datetime(1997, 11, 21, 15, 55, 6, tzinfo=datetime.UTC),
        )
