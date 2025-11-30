import pytest

from adjunct.netstrings import MalformedNetstringError, parse


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"", []),
        (b"0:,", [b""]),
        (b"1:a,", [b"a"]),
        (b"2:ab,", [b"ab"]),
        (b"10:abcdezxcvb,", [b"abcdezxcvb"]),
        (b"0:,0:,", [b"", b""]),
        (b"1:a,1:a,", [b"a", b"a"]),
        (b"2:ab,2:ab,", [b"ab", b"ab"]),
    ],
)
def test_good(data, expected):
    assert parse(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        b"12345678901:b,",
        b"5:abcd,",
        b"0:",
        b"01:b,",
        b"a:b,",
        b"5:abcd",
        b"5:abcde",
    ],
)
def test_malformed(data):
    with pytest.raises(MalformedNetstringError):
        parse(data)
