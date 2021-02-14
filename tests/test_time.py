import datetime
import unittest

from adjunct import time


class TimeTest(unittest.TestCase):
    def test_date(self):
        self.assertEqual(
            time.date("2033-05-18 03:33:20"),
            "2033-05-18T03:33:20+0000",
        )

    def test_tz(self):
        ist = datetime.timezone(datetime.timedelta(hours=-1), "IST")
        self.assertEqual(
            time.date("2033-05-18 03:33:20", tz=ist),
            "2033-05-18T03:33:20-0100",
        )
