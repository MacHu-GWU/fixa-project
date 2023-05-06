# -*- coding: utf-8 -*-

import typing as T
import os
import contextlib
from pathlib import Path


@contextlib.contextmanager
def temp_cwd(path: T.Union[str, Path]):
    """
    Temporarily set the current working directory (CWD) and automatically
    switch back when it's done.

    Example:

    .. code-block:: python

        with temp_cwd(Path("/path/to/target/working/directory")):
            # do something
    """
    cwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield path
    finally:
        os.chdir(cwd)
