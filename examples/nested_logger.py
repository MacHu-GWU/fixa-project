# -*- coding: utf-8 -*-

import json
from fixa.nest_logger import (
    format_line,
    format_ruler,
    NestedLogger,
)

logger = NestedLogger(name="nested_logger_demo")

logger.info("hello")
logger.info("hello", pipe="+")

print(format_ruler("start"))
print(
    format_ruler(
        "start",
        nest=1,
        _pipes=[
            "# ",
        ],
    )
)

data = {"a": {"b": {"c": 3}}}
logger.info(json.dumps(data, indent=4))

with logger.pipe("& "):
    logger.ruler("start 0")
    logger.info("hello 0")
    with logger.nested(pipe="#"):
        logger.ruler("start 1")
        logger.info("hello 1")
        with logger.nested(pipe="*"):
            logger.ruler("start 2")
            logger.info("hello 2")
            logger.ruler("end 2")
        logger.ruler("end 1")
    logger.ruler("end 0")


@logger.pretty_log()
def func1():
    logger.info("log1")


func1()


@logger.pretty_log(nest=1)
def func2():
    logger.info("log1")


func2()


@logger.pretty_log(nest=2)
def func3():
    logger.info("log1")


func3()


@logger.pretty_log(corner="@", pipe="@ ")
def func1():
    logger.info("run func1")
    logger.info(json.dumps({"a": 1}, indent=4))


@logger.pretty_log(corner="#", pipe="# ")
def func2():
    logger.info("run func2")
    with logger.nested():
        func1()
    logger.info(json.dumps({"b": 2}, indent=4))


@logger.pretty_log(corner="*", pipe="* ")
def func3():
    logger.info("run func3")
    with logger.nested():
        func2()
    logger.info(json.dumps({"c": 3}, indent=4))


func3()
