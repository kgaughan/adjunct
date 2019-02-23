import unittest

from adjunct.netstrings import parse, MalformedNetstring


class NetstringReaderTest(unittest.TestCase):

    def test_empty(self):
        self.assertListEqual(parse(b""), [])

    def test_single(self):
        self.assertListEqual(parse(b"0:,"), [b""])
        self.assertListEqual(parse(b"1:a,"), [b"a"])
        self.assertListEqual(parse(b"2:ab,"), [b"ab"])

    def test_series(self):
        self.assertListEqual(parse(b"0:,0:,"), [b"", b""])
        self.assertListEqual(parse(b"1:a,1:a,"), [b"a", b"a"])
        self.assertListEqual(parse(b"2:ab,2:ab,"), [b"ab", b"ab"])

    def test_length_limit(self):
        with self.assertRaises(MalformedNetstring):
            parse(b"12345678901:b,")

    def test_leading_zero(self):
        with self.assertRaises(MalformedNetstring):
            parse(b"01:b,")

    def test_bad_length(self):
        with self.assertRaises(MalformedNetstring):
            parse(b"a:b,")

    def test_truncation(self):
        with self.assertRaises(MalformedNetstring):
            parse(b"5:abcd")
        with self.assertRaises(MalformedNetstring):
            parse(b"0:")
        with self.assertRaises(MalformedNetstring):
            parse(b"5:abcde")
