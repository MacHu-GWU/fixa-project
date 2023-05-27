# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
from fixa.git_cli import (
    locate_dir_repo,
    get_git_branch_from_git_cli,
    get_git_commit_id_from_git_cli,
    get_commit_message_by_commit_id,
)

dir_repo = Path(__file__).parent.parent


def test_locate_dir_repo():
    assert locate_dir_repo(Path(__file__)) == dir_repo
    with pytest.raises(FileNotFoundError):
        locate_dir_repo(Path.home())


def test_get_git_branch_from_git_cli():
    branch = get_git_branch_from_git_cli(dir_repo)


def test_get_git_commit_id_from_git_cli():
    commit_id = get_git_commit_id_from_git_cli(dir_repo)


def test_get_commit_message_by_commit_id():
    commit_id = get_git_commit_id_from_git_cli(dir_repo)
    commit_message = get_commit_message_by_commit_id(dir_repo, commit_id)


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.git_cli", preview=False)
