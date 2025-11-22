import datetime

from adjunct import time


def test_parse_dt():
    expected = datetime.datetime(
        year=2033,
        month=5,
        day=18,
        hour=3,
        minute=33,
        second=20,
        tzinfo=datetime.UTC,
    )
    assert time.parse_dt("2033-05-18 03:33:20") == expected


def test_tz():
    ist = datetime.timezone(datetime.timedelta(hours=-1), "IST")
    assert time.to_iso_date("2033-05-18 03:33:20", tz=ist) == "2033-05-18T03:33:20-01:00"
