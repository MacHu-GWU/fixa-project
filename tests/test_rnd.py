# -*- coding: utf-8 -*-

import pytest
from fixa.rnd import rand_str, rand_hexstr, rand_alphastr, rand_pwd


def test_rnd():
    rand_str(32)
    rand_hexstr(12)
    rand_alphastr(12)
    rand_pwd(12)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
