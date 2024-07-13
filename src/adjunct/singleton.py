import contextlib
import fcntl


class MutexError(Exception):
    """
    Failed to lock a file.
    """


@contextlib.contextmanager
def mutex(filename: str):
    """
    Lock a mutex file.

    This can be used to prevent scripts from having more than one instance of
    themselves running at the same time as follows::

        if __name__ == "__main__":
            with mutex(__file__):
                main()
    """
    with open(filename, "rb") as fh:
        try:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                raise MutexError(f"Failed to lock {filename}")
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
