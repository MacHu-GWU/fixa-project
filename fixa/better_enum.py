# -*- coding: utf-8 -*-

import typing as T
import enum


class BetterIntEnum(int, enum.Enum):
    @classmethod
    def get_by_name(cls, name: str):
        return cls[name]

    @classmethod
    def get_by_value(cls, value: int):
        return cls(value)

    @classmethod
    def is_valid_name(cls, name: str) -> bool:
        try:
            _ = cls[name]
            return True
        except KeyError:
            return False

    @classmethod
    def is_valid_value(cls, value: int) -> bool:
        try:
            _ = cls(value)
            return True
        except ValueError:
            return False

    @classmethod
    def ensure_is_valid_value(cls, value):
        if cls.is_valid_value(value) is False:
            raise ValueError(f"Invalid {cls.__name__}: {value!r}")

    @classmethod
    def ensure_int(cls, value: T.Union[int, "BetterIntEnum"]) -> int:
        if isinstance(value, cls):
            return value.value
        else:
            return cls(value).value

    @classmethod
    def value_list(cls) -> T.List[int]:
        return [i.value for i in cls]


class BetterStrEnum(str, enum.Enum):
    """ """

    @classmethod
    def get_by_name(cls, name: str):
        return cls[name]

    @classmethod
    def get_by_value(cls, value: str):
        return cls(value)

    @classmethod
    def is_valid_name(cls, name: str) -> bool:
        try:
            _ = cls[name]
            return True
        except KeyError:
            return False

    @classmethod
    def is_valid_value(cls, value: str) -> bool:
        try:
            _ = cls(value)
            return True
        except ValueError:
            return False

    @classmethod
    def ensure_is_valid_value(cls, value):
        if cls.is_valid_value(value) is False:
            raise ValueError(f"Invalid {cls.__name__}: {value!r}")

    @classmethod
    def ensure_str(cls, value: T.Union[str, "BetterStrEnum"]) -> str:
        if isinstance(value, cls):
            return value.value
        else:
            return cls(value).value

    @classmethod
    def value_list(cls) -> T.List[str]:
        return [i.value for i in cls]
