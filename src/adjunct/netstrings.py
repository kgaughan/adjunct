"""
Simple netstring_ reader implemented as a generator.

.. _netstring: http://cr.yp.to/proto/netstrings.txt
"""

import io
import typing as t


class MalformedNetstringError(Exception):
    """
    Raised when the netstring reader hits a parser error in the stream.
    """


def parse(ns: bytes) -> t.Sequence[bytes]:
    """
    Parse a bytestring of netstrings.
    """
    with io.BytesIO(ns) as fh:
        return list(netstring_reader(fh))


def netstring_reader(fd: io.BufferedIOBase) -> t.Iterable[bytes]:  # noqa: C901
    """
    Reads a sequence of netstrings from the given file object.
    """
    while True:
        buffered = b""
        n = 0
        while True:
            ch = fd.read(1)
            if ch == b"":
                return
            if ch == b":":
                break
            n += 1
            if n > 10:
                raise MalformedNetstringError("Length too long")
            if ch == b"0" and buffered == b"":
                if fd.read(1) != b":":
                    raise MalformedNetstringError("Disallowed leading zero")
                buffered = ch
                break
            buffered += ch
        try:
            size = int(buffered.decode(), 10)
        except ValueError:
            raise MalformedNetstringError("Bad length") from None
        payload = b""
        while size > 0:
            buffered = fd.read(size)
            if buffered == b"":
                raise MalformedNetstringError("Connection closed too early")
            payload += buffered
            size -= len(buffered)
        if fd.read(1) != b",":
            raise MalformedNetstringError("Missing trailing comma")
        yield payload
