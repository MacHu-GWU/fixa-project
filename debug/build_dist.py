# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from fixa.build_dist import (
    build_dist_with_python,
    build_dist_with_python_build,
    build_dist_with_poetry_build,
)

dir_project_root = Path(__file__).absolute().parent.parent
path_bin_python = Path(sys.executable)
path_bin_poetry = "poetry"

build_dist_with_python(dir_project_root, path_bin_python, True)
build_dist_with_python_build(dir_project_root, path_bin_python, True)
build_dist_with_poetry_build(dir_project_root, path_bin_poetry, True)
