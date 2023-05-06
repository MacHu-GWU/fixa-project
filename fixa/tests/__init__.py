# -*- coding: utf-8 -*-

from pathlib import Path
from ..pytest_cov_helper import run_cov_test as _run_cov_test

dir_project_root = Path(__file__).absolute().parent.parent.parent
dir_htmlcov = dir_project_root / ".htmlcov"


def run_cov_test(
    script: str,
    module: str,
    preview: bool = False,
    is_folder: bool = False,
):
    _run_cov_test(
        script=script,
        module=module,
        root_dir=f"{dir_project_root}",
        htmlcov_dir=f"{dir_htmlcov}",
        preview=preview,
        is_folder=is_folder,
    )
