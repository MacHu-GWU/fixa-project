# -*- coding: utf-8 -*-

import pytest
from fixa import binarysearch as bs


def test_bsearch():
    sorted_list = [0, 1, 2, 3]
    assert bs.find_index(sorted_list, 2) == 2
    assert bs.find_lt(sorted_list, 2.5) == 2
    assert bs.find_le(sorted_list, 2.0) == 2
    assert bs.find_gt(sorted_list, 0.5) == 1
    assert bs.find_ge(sorted_list, 1.0) == 1

    with pytest.raises(ValueError):
        bs.find_index(sorted_list, -1)

    with pytest.raises(ValueError):
        bs.find_lt(sorted_list, -1)

    with pytest.raises(ValueError):
        bs.find_le(sorted_list, -1)

    with pytest.raises(ValueError):
        bs.find_gt(sorted_list, 9)

    with pytest.raises(ValueError):
        bs.find_ge(sorted_list, 9)


def test_find_last_true():
    sorted_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def true_criterion(item):
        return item <= -1

    with pytest.raises(ValueError):
        bs.find_last_true(sorted_list, true_criterion)

    def true_criterion(item):
        return item <= 100

    assert bs.find_last_true(sorted_list, true_criterion) == 9

    def true_criterion(item):
        return item <= 5

    assert bs.find_last_true(sorted_list, true_criterion) == 5


def test_find_nearest():
    sorted_list = list(range(10))
    assert bs.find_nearest(sorted_list, 4.4) == 4
    assert bs.find_nearest(sorted_list, 4.5) == 4
    assert bs.find_nearest(sorted_list, 4.6) == 5
    assert bs.find_nearest(sorted_list, -10) == 0
    assert bs.find_nearest(sorted_list, 100) == 9


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.binarysearch", preview=False)
