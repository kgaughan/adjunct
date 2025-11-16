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
            except OSError:
                raise MutexError(f"Failed to lock {filename}") from None
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def main():
    import time  # noqa: PLC0415

    while True:
        print("Sleeping for a few seconds...")  # noqa: T201
        time.sleep(5)


if __name__ == "__main__":
    try:
        with mutex(__file__):
            main()
    except MutexError:
        print("You can only run one copy of this script at once.")  # noqa: T201
