import os.path

import pytest

from adjunct import discovery, ogp

HERE = os.path.dirname(__file__)


@pytest.fixture(scope="session")
def ogp_properties():
    with open(os.path.join(HERE, "ogp.html"), "rb") as fh:
        raw = discovery.Extractor.extract(fh).properties
    return (raw, ogp.parse(raw))


def test_size(ogp_properties):
    raw, parsed = ogp_properties
    assert len(raw) == 11
    assert len(parsed) == 7


def test_access(ogp_properties):
    _, parsed = ogp_properties
    assert len(list(ogp.find(parsed, "type", "song"))) == 1


def test_invalid(ogp_properties):
    _, parsed = ogp_properties
    assert not list(ogp.find(parsed, "audio"))


def test_video(ogp_properties):
    _, parsed = ogp_properties
    videos = list(ogp.find(parsed, "video"))
    assert len(videos) == 1
    assert videos[0].value == videos[0].metadata["secure_url"]
    assert set(videos[0].metadata.keys()) == {"secure_url", "type", "width", "height"}


def test_meta(ogp_properties):
    _, parsed = ogp_properties
    meta = ogp.to_meta(parsed)
    with open(os.path.join(HERE, "ogp-minotaur-shock.html")) as fh:
        expected = fh.read().strip()
    assert meta == expected


def test_str(ogp_properties):
    _, parsed = ogp_properties
    first = parsed[0]
    assert str(first) == first.to_meta()


def test_single_property_to_meta():
    prop = ogp.Property(
        type_="title",
        value="Example Title",
        metadata={"lang": "en", "alternate": "true"},
    )
    meta = ogp.to_meta(prop)
    expected = "\n".join(  # noqa: FLY002
        [
            '<meta property="og:title" content="Example Title">',
            '<meta property="og:title:lang" content="en">',
            '<meta property="og:title:alternate" content="true">',
        ]
    )
    assert meta == expected


def test_bad_metadata_handling():
    properties = [
        ("og:title", "Example Title"),
        ("og:title:lang", "en"),
        ("og:description:badmeta", "This should be ignored"),
        ("og:description", "An example description."),
    ]
    parsed = ogp.parse(properties)
    assert len(parsed) == 2
    assert parsed[0].type_ == "title"
    assert parsed[0].metadata == {"lang": "en"}
    assert parsed[1].type_ == "description"
    assert parsed[1].metadata == {}
