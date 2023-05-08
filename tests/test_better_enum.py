# -*- coding: utf-8 -*-

import pytest
from fixa.better_enum import (
    BetterIntEnum,
    BetterStrEnum,
)


class CodeEnum(BetterIntEnum):
    succeeded = 1
    failed = 0


class TestBetterIntEnum:
    def test(self):
        assert CodeEnum.succeeded == 1
        assert 0 < CodeEnum.succeeded < 2
        assert (CodeEnum.succeeded + 1) == 2
        assert {CodeEnum.succeeded, CodeEnum.failed} == {0, 1}

    def test_get_by_name(self):
        assert CodeEnum.get_by_name("succeeded") is CodeEnum.succeeded
        with pytest.raises(KeyError):
            CodeEnum.get_by_name(1)

    def test_get_by_value(self):
        assert CodeEnum.get_by_value(1) is CodeEnum.succeeded
        with pytest.raises(ValueError):
            CodeEnum.get_by_value("succeeded")

    def test_is_valid_name(self):
        assert CodeEnum.is_valid_name("succeeded") is True
        assert CodeEnum.is_valid_name("SUCCEEDED") is False
        assert CodeEnum.is_valid_name(1) is False

    def test_is_valid_value(self):
        assert CodeEnum.is_valid_value("succeeded") is False
        assert CodeEnum.is_valid_value("SUCCEEDED") is False
        assert CodeEnum.is_valid_value(1) is True

    def test_ensure_is_valid_value(self):
        CodeEnum.ensure_is_valid_value(1)
        with pytest.raises(ValueError):
            CodeEnum.ensure_is_valid_value("succeeded")

    def test_ensure_str(self):
        assert CodeEnum.ensure_int(1) == 1
        assert CodeEnum.ensure_int(CodeEnum.succeeded) == 1
        assert isinstance(CodeEnum.ensure_int(1), int)
        assert isinstance(CodeEnum.ensure_int(CodeEnum.succeeded), int)

        with pytest.raises(ValueError):
            CodeEnum.ensure_int(9)

    def test_get_names_values(self):
        assert CodeEnum.get_names() == ["succeeded", "failed"]
        assert CodeEnum.get_values() == [1, 0]


class StatusEnum(BetterStrEnum):
    succeeded = "SUCCEEDED"
    failed = "FAILED"


class TestBetterStrEnum:
    def test(self):
        assert StatusEnum.succeeded.replace("SUC", "") == "CEEDED"
        assert StatusEnum.succeeded == "SUCCEEDED"
        assert f"it is {StatusEnum.succeeded}" == "it is SUCCEEDED"
        assert {StatusEnum.succeeded, StatusEnum.failed} == {"SUCCEEDED", "FAILED"}

    def test_get_by_name(self):
        assert StatusEnum.get_by_name("succeeded") is StatusEnum.succeeded
        with pytest.raises(KeyError):
            StatusEnum.get_by_name("SUCCEEDED")

    def test_get_by_value(self):
        assert StatusEnum.get_by_value("SUCCEEDED") is StatusEnum.succeeded
        with pytest.raises(ValueError):
            StatusEnum.get_by_value("succeeded")

    def test_is_valid_name(self):
        assert StatusEnum.is_valid_name("succeeded") is True
        assert StatusEnum.is_valid_name("SUCCEEDED") is False

    def test_is_valid_value(self):
        assert StatusEnum.is_valid_value("succeeded") is False
        assert StatusEnum.is_valid_value("SUCCEEDED") is True

    def test_ensure_is_valid_value(self):
        StatusEnum.ensure_is_valid_value("SUCCEEDED")
        with pytest.raises(ValueError):
            StatusEnum.ensure_is_valid_value("succeeded")

    def test_ensure_str(self):
        assert StatusEnum.ensure_str("SUCCEEDED") == "SUCCEEDED"
        assert StatusEnum.ensure_str(StatusEnum.succeeded) == "SUCCEEDED"
        assert isinstance(StatusEnum.ensure_str("SUCCEEDED"), str)
        assert isinstance(StatusEnum.ensure_str(StatusEnum.succeeded), str)

        with pytest.raises(ValueError):
            StatusEnum.ensure_str("succeeded")

    def test_value_list(self):
        assert StatusEnum.get_names() == ["succeeded", "failed"]
        assert StatusEnum.get_values() == ["SUCCEEDED", "FAILED"]


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.better_enum", preview=False)
