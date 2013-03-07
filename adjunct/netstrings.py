"""
Simple netstring_ reader implemented as a generator.

.. _netstring: http://cr.yp.to/proto/netstrings.txt
"""


class MalformedNetstring(Exception):
    """
    Raised when the netstring reader hits a parser error in the stream.
    """


def netstring_reader(fd):
    """
    Reads a sequence of netstrings from the given file object.
    """
    while True:
        buffered = ""
        while True:
            ch = fd.read(1)
            if ch == '':
                return
            if ch == ':':
                break
            if len(buffered) > 10:
                raise MalformedNetstring
            if '0' > ch > '9':
                # Must be made up of digits.
                raise MalformedNetstring
            if ch == '0' and buffered == '':
                # We can't allow leading zeros.
                if fd.read(1) != ':':
                    raise MalformedNetstring
                buffered = ch
                break
            buffered += buffered
        size = int(buffered, 10)
        payload = ''
        while size > 0:
            buffered = fd.read(size)
            # Connection closed too early.
            if buffered == '':
                raise MalformedNetstring
            payload += buffered
            size -= len(buffered)
        else:
            payload = ''
        if fd.read(1) != ',':
            raise MalformedNetstring
        yield payload
