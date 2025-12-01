import datetime
import os.path

import pytest

from adjunct import opml

HERE = os.path.dirname(__file__)


def test_parse_file():
    with open(os.path.join(HERE, "sample.opml")) as fh:
        doc = opml.parse(fh)

    assert doc is not None
    assert doc.root
    assert len(doc.attrs) == 1
    assert doc.attrs["title"] == "Sample OPML file"
    assert len(doc) == 3

    # Check the top-level categories.
    assert len(doc[0]) == 2
    assert len(doc[1]) == 1
    assert len(doc[2]) == 1

    # Check the last category and the one feed within it.
    assert doc[2].attrs["text"] == "Personal"
    cant_hack = doc[2][0]
    # 5, because it includes isComment and isBreakpoint implicitly
    assert len(cant_hack.attrs) == 5
    assert len(cant_hack) == 0
    assert cant_hack.attrs["text"] == "Can't Hack"
    assert cant_hack.attrs["type"] == "rss"
    assert cant_hack.attrs["xmlUrl"] == "https://i.canthack.it/feeds/all.xml"
    assert cant_hack.attrs["isComment"] == "false"
    assert cant_hack.attrs["isBreakpoint"] == "false"


def test_exception():
    with pytest.raises(opml.OpmlError):
        opml.parse_string('<?xml version="1.0" encoding="UTF-8"?><opml version="1.0"><outline/></opml>')


def test_date_parse():
    # Note: the resulting date is in UTC.
    expected = datetime.datetime(1997, 11, 21, 15, 55, 6, tzinfo=datetime.UTC)
    assert opml.parse_timestamp("Fri, 21 Nov 1997 09:55:06 -0600") == expected
