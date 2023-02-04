# -*- coding: utf-8 -*-

import pytest
import time
from fixa.nest_logger import logger, ruler, AlignEnum


def test_ruler():
    print("")

    ruler("Hello")
    ruler("Hello", length=40)
    ruler("Hello", char="=")
    ruler("Hello", corner="+")
    ruler("Hello", align=AlignEnum.left)
    ruler("Hello", align=AlignEnum.right)
    ruler("Hello", left_padding=10)
    ruler("Hello", right_padding=10)


def test_nested_logger_nested_context_manager():
    print("")

    with logger.nested(0):
        logger.ruler("nested 0 start")
        logger.info("nested 0")

        with logger.nested(1):
            logger.ruler("nested 1 start")
            logger.info("nested 1")
            logger.ruler("nested 1 end")

        logger.ruler("nested 0 end")


def test_nested_logger_pretty_log_decorator():
    print("")

    @logger.pretty_log(nest=1)
    def my_func2(name: str):
        time.sleep(1)
        logger.info(f"{name} do something in my func 2")

    @logger.pretty_log()
    def my_func1(name: str):
        time.sleep(1)
        logger.info(f"{name} do something in my func 1")
        my_func2(name="bob")

    my_func1(name="alice")


def test_nested_logger_pretty_log_decorator_error_case():
    print("")

    @logger.pretty_log()
    def my_func():
        time.sleep(1)
        logger.info(f"start doing something ...")
        raise Exception
        logger.info(f"end doing something ...")

    with pytest.raises(Exception):
        my_func()


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
