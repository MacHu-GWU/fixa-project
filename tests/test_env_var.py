# -*- coding: utf-8 -*-

import os
from fixa.env_var import (
    temp_env_var,
    normalize_env_var_name,
)


def test_temp_env_var():
    os.environ["TEST_1"] = "a"
    os.environ["TEST_2"] = "b"

    with temp_env_var({"TEST_1": "aaa", "TEST_2": None, "TEST_3": "ccc"}):
        assert os.environ["TEST_1"] == "aaa"
        assert "TEST_2" not in os.environ
        assert os.environ["TEST_3"] == "ccc"
    assert os.environ["TEST_1"] == "a"
    assert os.environ["TEST_2"] == "b"
    assert "TEST_3" not in os.environ

    try:
        with temp_env_var({"TEST_1": "aaa", "TEST_2": None, "TEST_3": "ccc"}):
            _ = 1
            raise Exception
    except Exception:
        pass
    assert os.environ["TEST_1"] == "a"
    assert os.environ["TEST_2"] == "b"
    assert "TEST_3" not in os.environ


def test_normalize_env_var_name():
    assert normalize_env_var_name("hello-world") == "HELLO_WORLD"
    assert normalize_env_var_name("hello world") == "HELLO_WORLD"


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.env_var", preview=False)
