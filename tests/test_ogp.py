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
    assert len(list(ogp.find(parsed, "audio"))) == 0


def test_video(ogp_properties):
    _, parsed = ogp_properties
    videos = list(ogp.find(parsed, "video"))
    assert len(videos) == 1
    assert videos[0].value == videos[0].metadata["secure_url"]
    assert set(videos[0].metadata.keys()) == {"secure_url", "type", "width", "height"}


def test_meta(ogp_properties):
    _, parsed = ogp_properties
    with open(os.path.join(HERE, "ogp-minotaur-shock.html")) as fh:
        expected = fh.read().strip()
    meta = ogp.to_meta(parsed)
    assert meta == expected
