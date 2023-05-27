# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
from fixa.better_pathlib import temp_cwd


def test_temp_cwd():
    dir_here = Path(__file__).absolute().parent
    p = dir_here.parent.parent.parent  # the parent of fix-project

    assert Path.cwd() != p
    with temp_cwd(p):
        assert Path.cwd() == p
    assert Path.cwd() != p

    assert Path.cwd() != p
    with temp_cwd(p):
        assert Path.cwd() == p
        with pytest.raises(Exception):
            raise Exception()
    assert Path.cwd() != p

    with pytest.raises(NotADirectoryError):
        with temp_cwd(__file__):
            pass


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.better_pathlib", preview=False)
