import io

import pytest

from adjunct import html


def test_empty():
    root = html.parse("")
    assert len(root) == 0
    assert root.attrs == {}


def test_simple():
    root = html.parse("<a>")
    assert len(root) == 1
    assert root[0].tag == "a"


def test_simple_nesting():
    root = html.parse("<b><a>")
    assert len(root) == 1
    assert root[0].tag == "b"
    assert root[0][0].tag == "a"


def test_self_closing():
    root = html.parse("<br><hr>")
    assert len(root) == 2
    assert root[0].tag == "br"
    assert root[1].tag == "hr"


def test_text_embedding():
    root = html.parse("a<br>b<hr>c")
    assert len(root) == 5
    assert isinstance(root[0], str)
    assert root[0] == "a"
    assert isinstance(root[1], html.Element)
    assert root[1].tag == "br"
    assert isinstance(root[2], str)
    assert root[2] == "b"
    assert isinstance(root[3], html.Element)
    assert root[3].tag == "hr"
    assert isinstance(root[4], str)
    assert root[4] == "c"


@pytest.mark.parametrize(
    ("src", "length", "expected"),
    [
        ("<br/>", 1, "<br>"),
        ("<br></br>", 1, "<br>"),
        ("<p><div></p></div>", 1, "<p><div></div></p>"),
        ("<a>", 1, "<a></a>"),
        ('<a href="foo">bar</a>', 1, '<a href="foo">bar</a>'),
        ("<a name>bar</a>", 1, "<a name>bar</a>"),
    ],
)
def test_serialisation(src, length, expected):
    root = html.parse(src)
    assert len(root) == length
    with io.StringIO() as fh:
        root.serialize(fh)
        assert fh.getvalue() == expected


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
