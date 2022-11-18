import contextlib
import fcntl


class MutexException(Exception):
    """
    Failed to lock a file.
    """


@contextlib.contextmanager
def mutex(filename):
    """
    Lock a mutex file.

    This can be used to prevent scripts from having more than one instance of
    themselves running at the same time as follows::

        if __name__ == "__main__":
            with mutex(__file__):
                main()
    """
    with open(filename, "r") as fh:
        try:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                raise MutexException(f"Failed to lock {filename}")
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
