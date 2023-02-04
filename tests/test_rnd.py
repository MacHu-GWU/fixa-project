# -*- coding: utf-8 -*-

import pytest
from fixa.rnd import rand_str, rand_hexstr, rand_alphastr, rand_pwd


def test_rnd():
    rand_str(32)

    rand_hexstr(12)
    rand_hexstr(12, lower=False)

    rand_alphastr(12, lower=True, upper=True)
    rand_alphastr(12, lower=False, upper=True)
    rand_alphastr(12, lower=True, upper=False)

    rand_pwd(12)
    rand_pwd(12, special_char=False)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
