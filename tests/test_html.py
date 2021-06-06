import io
import unittest

from adjunct import html


def parse(fixture):
    parser = html.Parser()
    parser.feed(fixture)
    parser.close()
    return parser.root


class TestParser(unittest.TestCase):
    def test_empty(self):
        root = parse("")
        self.assertEqual(len(root), 0)
        self.assertDictEqual(root.attrs, {})

    def test_simple(self):
        root = parse("<a>")
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, "a")

    def test_simple_nesting(self):
        root = parse("<b><a>")
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, "b")
        self.assertEqual(root[0][0].tag, "a")

    def test_self_closing(self):
        root = parse("<br><hr>")
        self.assertEqual(len(root), 2)
        self.assertEqual(root[0].tag, "br")
        self.assertEqual(root[1].tag, "hr")

    def test_text_embedding(self):
        root = parse("a<br>b<hr>c")
        self.assertEqual(len(root), 5)
        self.assertIsInstance(root[0], str)
        self.assertEqual(root[0], "a")
        self.assertIsInstance(root[1], html.Element)
        self.assertEqual(root[1].tag, "br")
        self.assertIsInstance(root[2], str)
        self.assertEqual(root[2], "b")
        self.assertIsInstance(root[3], html.Element)
        self.assertEqual(root[3].tag, "hr")
        self.assertIsInstance(root[4], str)
        self.assertEqual(root[4], "c")


class TestElement(unittest.TestCase):
    def assert_html(self, a, b):
        with io.StringIO() as fo:
            parse(a).serialize(fo)
            self.assertEqual(fo.getvalue(), b)

    def test_simple(self):
        self.assert_html("", "")
        self.assert_html("<a>", "<a></a>")
        self.assert_html("<br>", "<br>")

    def test_attrs(self):
        self.assert_html(
            '<a href="foo">bar</a>',
            '<a href="foo">bar</a>',
        )
        self.assert_html(
            "<a name>bar</a>",
            "<a name>bar</a>",
        )
