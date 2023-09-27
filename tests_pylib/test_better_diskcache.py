# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from pathlib import Path
from fixa.pylib.better_diskcache import TypedCache


dir_cache = Path(__file__).absolute().parent.joinpath(".cache")


class MyClass:
    def my_method(self):
        pass


typed_cache = TypedCache(str(dir_cache))


@typed_cache.typed_memoize()
def get() -> MyClass:
    return MyClass()


class TestTypedCache:
    def test(self):
        my_class = get()
        my_class.my_method()


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.pylib.better_diskcache", preview=False)
