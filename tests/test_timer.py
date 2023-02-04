# -*- coding: utf-8 -*-

import pytest
import time
import timeit
import random
from fixa.timer import BaseTimer, DateTimeTimer, TimeTimer, SerialTimer, timeit_wrapper


def sleep_random_time(min=0, max=1):
    length = random.random() * (max - min) + min
    time.sleep(length)


def setup_module(module):
    print("")


class TestDateTimeTime:
    def test(self):
        # usage1
        timer = DateTimeTimer(title="basic DateTimeTimer test")
        sleep_random_time()
        timer.end()

        # usage2
        with DateTimeTimer(title="basic DateTimeTimer test") as timer:
            sleep_random_time()

        # usage3
        timer = DateTimeTimer(title="basic DateTimeTimer test", start=False)
        timer.start()
        sleep_random_time()
        timer.end()

        # usage4
        with DateTimeTimer(title="basic DateTimeTimer test", start=False) as timer:
            sleep_random_time()

    def test_avg_error(self):
        measures = list()
        n = 20
        for i in range(n):
            with DateTimeTimer(display=False) as timer:
                time.sleep(0.1)
            measures.append(timer.elapsed)

        avg_error = (sum(measures) - 1) / n
        print("DateTimeTimer has %.6f seconds average error" % avg_error)


class TestTimeTimer:
    def test_avg_error(self):
        measures = list()
        n = 20
        for i in range(n):
            with TimeTimer(display=False) as timer:
                time.sleep(0.1)
            measures.append(timer.elapsed)

        avg_error = (sum(measures) - 1) / n
        print("TimeTimer has %.6f seconds average error" % avg_error)


class TestSerialTimer:
    def test(self):
        stimer = SerialTimer()
        with pytest.raises(RuntimeError):
            stimer.end()

        stimer.start(title="first measure")
        sleep_random_time()
        stimer.end()
        with pytest.raises(RuntimeError):
            stimer.end()

        stimer.start(title="second measure")
        sleep_random_time()
        stimer.click(title="third measure")
        sleep_random_time()
        stimer.click(title="fourth measure")
        stimer.end()

        assert isinstance(stimer.last, BaseTimer)
        assert isinstance(stimer.history, list)
        assert len(stimer.history) == 4
        assert isinstance(stimer.history[0], BaseTimer)


def test_timeit():
    def for_loop(n):
        for _ in range(n):
            pass

    n = 10**6
    number = 10
    # multiple time run total elapsed
    elapsed_measured_by_timeit = timeit.timeit(
        timeit_wrapper(for_loop, n), number=number
    )

    #
    with DateTimeTimer(display=False) as timer:
        for _ in range(number):
            for_loop(n)
    elapsed_measured_by_timer = timer.elapsed

    # simple time run elapsed
    st = time.time()
    for_loop(n)
    elapsed_single_run = time.time() - st

    assert elapsed_measured_by_timeit > elapsed_single_run * number / 2
    assert elapsed_measured_by_timer > elapsed_single_run * number / 2


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
