# -*- coding: utf-8 -*-

import os
import contextlib
from pathlib import Path


@contextlib.contextmanager
def temp_cwd(path: Path):
    """
    Temporarily set the current working directory (CWD) and automatically
    switch back when it's done.
    """
    cwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield path
    finally:
        os.chdir(cwd)
