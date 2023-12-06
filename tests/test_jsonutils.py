# -*- coding: utf-8 -*-

from fixa import jsonutils


def test_json_loads():
    text = """
    # this is a comment
    {
        "a": 1 // this is a comment
    }
    # this is a comment
    """
    assert jsonutils.json_loads(text) == {"a": 1}


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.jsonutils", preview=False)
