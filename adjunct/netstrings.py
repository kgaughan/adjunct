"""
Simple netstring_ reader implemented as a generator.

.. _netstring: http://cr.yp.to/proto/netstrings.txt
"""

import io


class MalformedNetstring(Exception):
    """
    Raised when the netstring reader hits a parser error in the stream.
    """


def parse(ns):
    """
    Parse a bytestring of netstrings.
    """
    with io.BytesIO(ns) as fh:
        return list(netstring_reader(fh))


def netstring_reader(fd):
    """
    Reads a sequence of netstrings from the given file object.
    """
    while True:
        buffered = b""
        while True:
            ch = fd.read(1)
            if ch == b"":
                return
            if ch == b":":
                break
            if len(buffered) > 10:
                raise MalformedNetstring("Length too long")
            if ch == b"0" and buffered == b"":
                if fd.read(1) != b":":
                    raise MalformedNetstring("Disallowed leading zero")
                buffered = ch
                break
            buffered += ch
        try:
            size = int(buffered.decode(), 10)
        except ValueError:
            raise MalformedNetstring("Bad length")
        payload = b""
        while size > 0:
            buffered = fd.read(size)
            if buffered == b"":
                raise MalformedNetstring("Connection closed too early")
            payload += buffered
            size -= len(buffered)
        if fd.read(1) != b",":
            raise MalformedNetstring("Missing trailing comma")
        yield payload
