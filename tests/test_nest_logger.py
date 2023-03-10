# -*- coding: utf-8 -*-

import pytest
import time
from fixa.nest_logger import (
    format_line,
    format_ruler,
    AlignEnum,
    NestedLogger,
)

logger = NestedLogger(name="nested_logger_unit_test")


def setup_module(module):
    print("")


def test_format_line():
    assert format_line("hello") == "| hello"
    assert format_line("hello", nest=1) == "| | hello"
    assert format_line("hello", nest=1, _pipes=["| ", "# "]) == "| # hello"

    assert format_line("hello", indent=1) == "|   hello"
    assert format_line("hello", indent=1, nest=1) == "| |   hello"
    assert format_line("hello", indent=1, nest=1, _pipes=["| ", "# "]) == "| #   hello"


def test_format_ruler():
    assert format_ruler("Hello", length=40) == (
        "---------------- Hello -----------------"
    )
    assert format_ruler("Hello", length=20) == ("------ Hello -------")
    assert format_ruler("Hello", char="=", length=40) == (
        "================ Hello ================="
    )
    assert format_ruler("Hello", corner="+", length=40) == (
        "+--------------- Hello ----------------+"
    )
    assert format_ruler("Hello", align=AlignEnum.left, length=40) == (
        "----- Hello ----------------------------"
    )
    assert format_ruler("Hello", align=AlignEnum.right, length=40) == (
        "---------------------------- Hello -----"
    )
    assert format_ruler("Hello", left_padding=3, align=AlignEnum.left, length=40) == (
        "--- Hello ------------------------------"
    )
    assert format_ruler("Hello", right_padding=3, align=AlignEnum.right, length=40) == (
        "------------------------------ Hello ---"
    )


def test_nested_context_manager():
    print("")
    logger.ruler("section 1")
    logger.info("hello 1")
    with logger.nested():
        logger.ruler("section 1.1")
        logger.info("hello 1.1")
        with logger.nested():
            logger.ruler("section 1.1.1")
            logger.info("hello 1.1.1")
            logger.ruler("section 1.1.1")
        logger.ruler("section 1.1")
    logger.ruler("section 1")


def test_disabled_context_manager():
    print("")

    logger.info("a")
    with logger.disabled(
        disable=True,
        # disable=False,
    ):
        logger.info("b")
    logger.info("c")


def test_pretty_log_decorator():
    print("")

    @logger.pretty_log(pipe="????")
    def run_build():
        time.sleep(1)
        logger.info("run build")

    @logger.pretty_log(pipe="????")
    def run_test():
        time.sleep(1)
        logger.info("run test")
        with logger.nested():
            run_build()

    @logger.pretty_log(pipe="????")
    def run_deploy():
        time.sleep(1)
        logger.info("run deploy")
        with logger.nested():
            run_test()

    run_deploy()


def test_block():
    print("")
    @logger.start_and_end(
        msg="My Function 1",
        start_emoji="????",
        end_emoji="????",
        pipe="????",
    )
    def my_func1(name: str):
        time.sleep(1)
        logger.info(f"{name} do something in my func 1")

    my_func1(name="alice")


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
