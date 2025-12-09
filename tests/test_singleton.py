import multiprocessing
import time

import pytest

from adjunct import singleton


def test_mutex():
    with singleton.mutex(__file__):  # noqa: SIM117
        with pytest.raises(singleton.MutexError):
            with singleton.mutex(__file__):
                pass


def worker(
    filename: str,
    result_queue: multiprocessing.Queue,
    sem,
):
    delay = 0.0125  # Tunable, if it needs to be
    try:
        with singleton.mutex(filename):
            if sem.acquire(timeout=delay):
                time.sleep(delay * 2)  # Hold the lock for a bit
                sem.release()
        result_queue.put(1)
    except singleton.MutexError:
        result_queue.put(0)


def test_mutex_in_two_processes(tmp_path):
    filename = tmp_path / "mutexfile"
    filename.touch()

    sem = multiprocessing.Semaphore(1)
    result_queue = multiprocessing.Queue()
    args = (str(filename), result_queue, sem)
    p1 = multiprocessing.Process(target=worker, args=args)
    p2 = multiprocessing.Process(target=worker, args=args)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    results = [result_queue.get() for _ in range(2)]
    assert results.count(1) == 1
    assert results.count(0) == 1
