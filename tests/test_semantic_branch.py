# -*- coding: utf-8 -*-

import pytest
import typing as T
from fixa.semantic_branch import (
    InvalidSemanticNameError,
    ensure_is_valid_semantic_name,
    is_certain_semantic_branch,
    is_main_branch,
    is_feature_branch,
    is_build_branch,
    is_doc_branch,
    is_fix_branch,
    is_release_branch,
    is_cleanup_branch,
    is_sandbox_branch,
    is_develop_branch,
    is_test_branch,
    is_int_branch,
    is_staging_branch,
    is_qa_branch,
    is_preprod_branch,
    is_prod_branch,
    is_blue_branch,
    is_green_branch,
    SemanticBranchRule,
)


def test_ensure_is_valid_semantic_name():
    ensure_is_valid_semantic_name("main")
    ensure_is_valid_semantic_name("feature")
    with pytest.raises(InvalidSemanticNameError):
        ensure_is_valid_semantic_name("feature-123")
    with pytest.raises(InvalidSemanticNameError):
        ensure_is_valid_semantic_name("release@1.2.3")
    with pytest.raises(InvalidSemanticNameError):
        ensure_is_valid_semantic_name("dev/description")


def test_is_certain_semantic_branch_edge_case():
    assert is_certain_semantic_branch("feat-123", ["feat"]) is True
    assert is_certain_semantic_branch("feat-123/description", ["feat"]) is True

    with pytest.raises(ValueError):
        is_certain_semantic_branch("main", ["feature-123"])


@pytest.mark.parametrize(
    "branch,func,flag",
    [
        ("main", is_main_branch, True),
        ("master", is_main_branch, True),
        ("Feat", is_feature_branch, True),
        ("Feature", is_feature_branch, True),
        ("build", is_build_branch, True),
        ("doc", is_doc_branch, True),
        ("fix", is_fix_branch, True),
        ("rls", is_release_branch, True),
        ("release", is_release_branch, True),
        ("clean", is_cleanup_branch, True),
        ("cleanup", is_cleanup_branch, True),
        ("Sbx", is_sandbox_branch, True),
        ("Sandbox", is_sandbox_branch, True),
        ("Dev", is_develop_branch, True),
        ("Develop", is_develop_branch, True),
        ("Tst", is_test_branch, True),
        ("test", is_test_branch, True),
        ("int", is_int_branch, True),
        ("stg", is_staging_branch, True),
        ("stage", is_staging_branch, True),
        ("staging", is_staging_branch, True),
        ("qa", is_qa_branch, True),
        ("preprod", is_preprod_branch, True),
        ("prd", is_prod_branch, True),
        ("prod", is_prod_branch, True),
        ("blue", is_blue_branch, True),
        ("green", is_green_branch, True),
    ],
)
def test_is_certain_semantic_branch(
    branch: str,
    func: T.Callable,
    flag: bool,
):
    assert func(branch) is flag


semantic_branch_rule = SemanticBranchRule(
    rules={
        "main": ["main", "master"],
        "feature": ["feat", "feature"],
    }
)


class TestSemanticBranchRule:
    def test_is_certain_semantic_branch(self):
        # fmt: off
        assert semantic_branch_rule.is_certain_semantic_branch(git_branch_name="main", semantic_name="main") is True
        assert semantic_branch_rule.is_certain_semantic_branch(git_branch_name="master", semantic_name="main") is True
        assert semantic_branch_rule.is_certain_semantic_branch(git_branch_name="feature/description", semantic_name="feature") is True
        assert semantic_branch_rule.is_certain_semantic_branch(git_branch_name="feature-123/description", semantic_name="feature") is True
        assert semantic_branch_rule.is_certain_semantic_branch(git_branch_name="major", semantic_name="main") is False

        with pytest.raises(InvalidSemanticNameError):
            semantic_branch_rule.is_certain_semantic_branch(git_branch_name="release", semantic_name="release")
        # fmt: on

    def test_parse_semantic_name(self):
        # fmt: off
        assert semantic_branch_rule.parse_semantic_name("feature/123") == "feature"
        assert semantic_branch_rule.parse_semantic_name("feature-123/123") == "feature"
        # this will hit cache
        assert semantic_branch_rule.parse_semantic_name("feature-123/123") == "feature"
        with pytest.raises(InvalidSemanticNameError):
            semantic_branch_rule.parse_semantic_name("release")
        # fmt: on


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.semantic_branch", preview=False)
