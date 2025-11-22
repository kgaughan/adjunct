import io
import unittest

from adjunct import html


class TestParser(unittest.TestCase):
    def test_empty(self):
        root = html.parse("")
        self.assertEqual(len(root), 0)
        self.assertDictEqual(root.attrs, {})

    def test_simple(self):
        root = html.parse("<a>")
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, "a")

    def test_simple_nesting(self):
        root = html.parse("<b><a>")
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, "b")
        self.assertEqual(root[0][0].tag, "a")

    def test_self_closing(self):
        root = html.parse("<br><hr>")
        self.assertEqual(len(root), 2)
        self.assertEqual(root[0].tag, "br")
        self.assertEqual(root[1].tag, "hr")

    def test_text_embedding(self):
        root = html.parse("a<br>b<hr>c")
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

    def test_startend(self):
        root = html.parse("<br/>")
        self.assertEqual(len(root), 1)
        with io.StringIO() as fh:
            root.serialize(fh)
            self.assertEqual(fh.getvalue(), "<br>")

    def test_closing_extra(self):
        root = html.parse("<br></br>")
        self.assertEqual(len(root), 1)
        with io.StringIO() as fh:
            root.serialize(fh)
            self.assertEqual(fh.getvalue(), "<br>")

    def test_unbalanced(self):
        root = html.parse("<p><div></p></div>")
        with io.StringIO() as fh:
            root.serialize(fh)
            self.assertEqual(fh.getvalue(), "<p><div></div></p>")


class TestElement(unittest.TestCase):
    def assert_html(self, a, b):
        with io.StringIO() as fh:
            html.parse(a).serialize(fh)
            self.assertEqual(fh.getvalue(), b)

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


def test_no_file_object_serialiser():
    expected = "<br>"
    fo = html.parse(expected).serialize()
    assert isinstance(fo, io.StringIO)
    assert fo.getvalue() == expected


def test_make_html():
    assert html.make("br", attrs={}) == "<br>"
    assert html.make("a", attrs={"href": "foo"}) == '<a href="foo"></a>'
    assert html.make("a", attrs={"href": "foo"}, close=False) == '<a href="foo">'
    assert html.make("input", attrs={"type": "checkbox", "disabled": None}) == '<input type="checkbox" disabled>'
