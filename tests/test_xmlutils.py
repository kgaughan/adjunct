import io

from adjunct.xmlutils import XMLBuilder


def test_basics():
    xml = XMLBuilder()
    assert xml.buffer is not None
    with xml.within("root", xmlns="tag:talideon.com,2013:test"):
        xml += "Before"
        with xml.within("leaf"):
            xml += "Within"
        xml += "After"
        xml.tag("leaf", "Another")
    assert (
        xml.as_string()
        == """<?xml version="1.0" encoding="utf-8"?>
<root xmlns="tag:talideon.com,2013:test">Before<leaf>Within</leaf>After<leaf>Another</leaf></root>"""
    )
    xml.close()
    assert xml.buffer is None


def test_own_buffer():
    buf = io.StringIO()
    xml = XMLBuilder(buf)
    assert xml.buffer is None
    with xml.within("root", xmlns="myns"):
        xml += "Body"
    assert xml.as_string() == ""
    assert (
        buf.getvalue()
        == """<?xml version="1.0" encoding="utf-8"?>
<root xmlns="myns">Body</root>"""
    )
    xml.close()


def test_attrs():
    xml = XMLBuilder()
    xml.root(xmlns="myns")
    assert (
        xml.as_string()
        == """<?xml version="1.0" encoding="utf-8"?>
<root xmlns="myns"></root>"""
    )
    xml.close()
