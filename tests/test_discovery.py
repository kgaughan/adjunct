import io

from adjunct import discovery


def test_empty():
    buf = io.BytesIO(
        b"""<!DOCTYPE html>
<html></html>"""
    )
    assert discovery.Extractor.extract(buf).collected == []


def test_one_link():
    buf = io.BytesIO(
        b"""<!DOCTYPE html>
<html>
    <head>
        <link rel="foo" href="bar">
    </head>
</html>"""
    )
    assert discovery.Extractor.extract(buf).collected == [{"href": "bar", "rel": "foo"}]


def test_one_link_with_base():
    buf = io.BytesIO(
        b"""<!DOCTYPE html>
<html>
    <head>
        <link rel="foo" href="bar">
        <base href="http://example.com/">
    </head>
</html>"""
    )
    assert discovery.Extractor.extract(buf).collected == [{"href": "http://example.com/bar", "rel": "foo"}]


def test_fetch_meta(fixture_app):
    links, properties = discovery.fetch_meta(f"{fixture_app}meta")
    assert links == [
        {"href": "http://example.com/", "rel": "bar"},
        {"href": f"{fixture_app}bar", "rel": "foo"},
    ]
    assert properties == [("og:title", "Example")]


def test_safe_slurp():
    data = b"Hello, world!\nThis is a test.\n"
    fh = io.BytesIO(data)
    result = "".join(discovery._safe_slurp(fh, chunk_size=4, encoding="utf-8"))
    assert result == data.decode("utf-8")


def test_safe_slurp_multibyte_utf8_across_chunks():
    # Use multi-byte UTF-8 characters (emoji and accented characters)
    text = "Hello \N{EARTH GLOBE EUROPE-AFRICA} \N{EN DASH} café \N{SMILING FACE WITH SMILING EYES}"
    data = text.encode("utf-8")

    # Use a chunk size smaller than some characters' byte length to force splits
    fh = io.BytesIO(data)
    result = "".join(discovery._safe_slurp(fh, chunk_size=2, encoding="utf-8"))
    assert result == text


def test_fix_attributes():
    assert discovery.fix_attributes(
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
