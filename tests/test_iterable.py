# -*- coding: utf-8 -*-

import pytest
import time
from fixa import iterable
from collections import OrderedDict


def test_flatten():
    assert list(iterable.flatten([[1, 2], [3, 4]])) == [1, 2, 3, 4]
    assert list(iterable.flatten([["a", "b"], ["c", "d"]])) == ["a", "b", "c", "d"]
    assert list(iterable.flatten(["ab", "cd"])) == ["a", "b", "c", "d"]


def test_flatten_performance():
    """
    **中文文档**

    测试是否用 itertools 实现的 flatten 性能要优于直接使用for循环实现.
    """

    def another_flatten(nested_iterable):
        """An intuitive implementation."""
        for iterable in nested_iterable:
            for i in iterable:
                yield i

    list_of_list = [list(range(1000)) for _ in range(1000)]

    st = time.perf_counter()
    list(iterable.flatten(list_of_list))
    elapsed1 = time.perf_counter() - st

    st = time.perf_counter()
    list(another_flatten(list_of_list))
    elapsed2 = time.perf_counter() - st

    assert elapsed1 < elapsed2


def test_flatten_all():
    nested_iterable = [[1, 2], "abc", [3, ["x", "y", "z"]], 4]
    assert list(iterable.flatten_all(nested_iterable)) == [
        1,
        2,
        "abc",
        3,
        "x",
        "y",
        "z",
        4,
    ]


def test_nth():
    array = [0, 1, 2]
    assert iterable.nth(array, 1) == 1
    assert iterable.nth(array, 3) == None


def test_take():
    array = [0, 1, 2]
    assert iterable.take(array, 0) == []
    assert iterable.take(array, 1) == [0]
    assert iterable.take(array, 2) == [0, 1]
    assert iterable.take(array, 3) == [0, 1, 2]


def test_pull():
    array = [0, 1, 2]
    assert iterable.pull(array, 0) == []
    assert iterable.pull(array, 1) == [
        2,
    ]
    assert iterable.pull(array, 2) == [1, 2]
    assert iterable.pull(array, 3) == [0, 1, 2]


def test_shuffled():
    array = list(range(1000))
    assert iterable.shuffled(range(1000)) != array


def test_grouper():
    l = [1, 2, 3]
    assert list(iterable.grouper(l, 2)) == [(1, 2), (3, None)]


def test_grouper_list():
    l = [1, 2, 3, 4]
    assert list(iterable.grouper_list(l, 2)) == [[1, 2], [3, 4]]

    l = [1, 2, 3, 4, 5]
    assert list(iterable.grouper_list(l, 2)) == [
        [1, 2],
        [3, 4],
        [
            5,
        ],
    ]


def test_grouper_dict():
    d = OrderedDict([("a", 1), ("b", 2), ("c", 3), ("d", 4)])
    assert list(iterable.grouper_dict(d, 2)) == [{"a": 1, "b": 2}, {"c": 3, "d": 4}]

    d = OrderedDict([("a", 1), ("b", 2), ("c", 3), ("d", 4), ("e", 5)])
    assert list(iterable.grouper_dict(d, 2)) == [
        {"a": 1, "b": 2},
        {"c": 3, "d": 4},
        {"e": 5},
    ]


def test_group_by():
    class Record:
        def __init__(self, product: str, date: str, sale: int):
            self.product = product
            self.date = date
            self.sale = sale

    records = [
        Record("apple", "2020-01-01", 10),
        Record("apple", "2020-01-02", 20),
        Record("apple", "2020-01-03", 30),
        Record("banana", "2020-01-01", 10),
        Record("banana", "2020-01-02", 20),
        Record("banana", "2020-01-03", 30),
    ]

    groups = iterable.group_by(records, get_key=lambda x: x.product)

    sales = [record.sale for record in groups["apple"]]
    sales.sort()
    assert sales == [10, 20, 30]
    sales = [record.sale for record in groups["banana"]]
    sales.sort()
    assert sales == [10, 20, 30]


def test_size_of_generator():
    """测试 :func:`~sfm.iterable.size_of_generator`  的性能。"""

    def number_generator():
        for i in range(1000 * 1000):
            yield i

    st = time.perf_counter()
    n1 = iterable.size_of_generator(number_generator(), memory_efficient=True)
    elapse1 = time.perf_counter() - st

    st = time.perf_counter()
    n2 = iterable.size_of_generator(number_generator(), memory_efficient=False)
    elapse2 = time.perf_counter() - st

    assert n1 == n2 == 1000 * 1000


def test_running_window():
    assert list(iterable.running_window([1, 2, 3, 4, 5], 3)) == [
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5],
    ]
    assert list(iterable.running_window([1, 2, 3], 3)) == [
        [1, 2, 3],
    ]
    with pytest.raises(ValueError):
        list(iterable.running_window([1, 2, 3], 4))


def test_cycle_running_window():
    assert list(iterable.cycle_running_window([1, 2, 3, 4, 5], 3)) == [
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5],
        [4, 5, 1],
        [5, 1, 2],
    ]
    assert list(iterable.cycle_running_window([1, 2, 3], 3)) == [
        [1, 2, 3],
        [2, 3, 1],
        [3, 1, 2],
    ]
    with pytest.raises(ValueError):
        list(iterable.cycle_running_window([1, 2, 3], 4))


def test_cycle_slice():
    array = [0, 1, 2, 3]
    assert iterable.cycle_slice(array, 1, 3) == [1, 2]
    assert iterable.cycle_slice(array, 3, 1) == [3, 0]
    assert iterable.cycle_slice(array, 0, 0) == [0, 1, 2, 3]
    assert iterable.cycle_slice(array, 2, 2) == [2, 3, 0, 1]

    assert iterable.cycle_slice(array, 5, -1) == [1, 2]

    array = [0]
    assert iterable.cycle_slice(array, 1, 2) == [0]

    with pytest.raises(ValueError):
        iterable.cycle_slice([], 1, 2)


def test_cycle_dist():
    assert iterable.cycle_dist(1, 23, 24) == 2
    assert iterable.cycle_dist(5, 13, 24) == 8
    assert iterable.cycle_dist(0, 4, 10) == 4
    assert iterable.cycle_dist(0, 6, 10) == 4


def test_cyclic_shift():
    array = [0, 1, 2]
    assert iterable.cyclic_shift(array, 0) == [0, 1, 2]
    assert iterable.cyclic_shift(array, 1) == [2, 0, 1]
    assert iterable.cyclic_shift(array, 2) == [1, 2, 0]
    assert iterable.cyclic_shift(array, -1) == [1, 2, 0]
    assert iterable.cyclic_shift(array, -2) == [2, 0, 1]


def test_shift_and_trim():
    array = [0, 1, 2]
    assert iterable.shift_and_trim(array, 0) == [0, 1, 2]
    assert iterable.shift_and_trim(array, 1) == [0, 1]
    assert iterable.shift_and_trim(array, -1) == [1, 2]
    assert iterable.shift_and_trim(array, 3) == []
    assert iterable.shift_and_trim(array, -3) == []
    assert iterable.shift_and_trim([], 3) == []


def test_shift_and_pad():
    array = [0, 1, 2]
    assert iterable.shift_and_pad(array, 0) == [0, 1, 2]
    assert iterable.shift_and_pad(array, 1) == [0, 0, 1]
    assert iterable.shift_and_pad(array, 2) == [0, 0, 0]
    assert iterable.shift_and_pad(array, 3) == [0, 0, 0]
    assert iterable.shift_and_pad(array, 3, None) == [None, None, None]

    assert iterable.shift_and_pad(array, -1) == [1, 2, 2]
    assert iterable.shift_and_pad(array, -2) == [2, 2, 2]
    assert iterable.shift_and_pad(array, -3) == [2, 2, 2]
    assert iterable.shift_and_pad(array, -3, None) == [None, None, None]

    assert iterable.shift_and_pad([], 3) == []


def test_difference():
    assert iterable.difference([0, 1, 3, 6, 10], 0) == [0, 0, 0, 0, 0]
    assert iterable.difference([0, 1, 3, 6, 10], 1) == [1, 2, 3, 4]
    assert iterable.difference([0, 1, 3, 6, 10], 2) == [3, 5, 7]

    with pytest.raises(ValueError):
        iterable.difference([1, 2, 3], -1)

    with pytest.raises(ValueError):
        iterable.difference([1, 2, 3], 3)


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.iterable", preview=False)
