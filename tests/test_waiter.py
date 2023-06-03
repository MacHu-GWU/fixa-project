# -*- coding: utf-8 -*-

import pytest
from fixa.waiter import Waiter

class TestWaiter:
    def test(self):
        # print("")
        # print("before waiter")

        for attempt, elapse in Waiter(
            delays=1,
            timeout=5,
            verbose=False,
            # verbose=True,
        ):
            # check if should jump out of the polling loop
            if elapse >= 3:
                print("")
                break

        # print("after waiter")

        with pytest.raises(TimeoutError):
            for _ in Waiter(
                delays=1,
                timeout=3,
                verbose=False,
                # verbose=True,
            ):
                pass



if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.waiter", preview=False)
