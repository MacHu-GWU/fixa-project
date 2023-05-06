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
        display = False
        # usage1
        timer = DateTimeTimer(title="basic DateTimeTimer test", display=display)
        sleep_random_time()
        timer.end()

        str(timer)

        # usage2
        with DateTimeTimer(title="basic DateTimeTimer test", display=display) as timer:
            sleep_random_time()

        # usage3
        timer = DateTimeTimer(
            title="basic DateTimeTimer test", start=False, display=display
        )
        timer.start()
        sleep_random_time()
        timer.end()

        # usage4
        with DateTimeTimer(
            title="basic DateTimeTimer test", start=False, display=display
        ) as timer:
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
        display = False
        stimer = SerialTimer()
        with pytest.raises(RuntimeError):
            stimer.end()

        stimer.start(title="first measure", display=display)
        sleep_random_time()
        stimer.end()
        with pytest.raises(RuntimeError):
            stimer.end()

        stimer.start(title="second measure", display=display)
        sleep_random_time()
        stimer.click(title="third measure", display=display)
        sleep_random_time()
        stimer.click(title="fourth measure", display=display)
        stimer.end()

        assert isinstance(stimer.last, BaseTimer)
        assert isinstance(stimer.history, list)
        assert len(stimer.history) == 4
        assert isinstance(stimer.history[0], BaseTimer)


def test_timeit():
    display = False

    def for_loop(n):
        for _ in range(n):
            pass

    n = 10**6
    number = 10

    # multiple time run total elapsed
    elapsed_measured_by_timeit = timeit.timeit(
        timeit_wrapper(for_loop, n), number=number
    )

    # measure by DateTimeTimer
    with DateTimeTimer(display=display) as timer:
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
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.timer", preview=False)
