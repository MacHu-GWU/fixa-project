# -*- coding: utf-8 -*-

"""
A dataclass-based dataframe.
"""

import typing as T
import dataclasses

ROW = T.TypeVar("ROW")


@dataclasses.dataclass
class TypedDataFrame(T.Generic[ROW]):
    """
    Example:

    .. code-block:: python

        >>> @dataclasses.dataclass
        ... class User:
        ...     id: int
        ...     name: str

        >>> @dataclasses.dataclass
        ... class UserDataFrame(TypedDataFrame[User]):
        ...     row_type = User

        >>> df = UserDataFrame(rows=[User(id=1, name="a"), User(id=2, name="b")])
        >>> df.columns
        ["id", "name"]
        >>> df.to_tuples()
        [(1, "a"), (2, "b")]
        >>> df.to_dicts()
        [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    """

    rows: T.List[ROW] = dataclasses.field(default_factory=list)

    row_type = None
    _columns = None

    @property
    def columns(self) -> T.List[str]:
        if self._columns is None:
            self._columns = [field.name for field in dataclasses.fields(self.row_type)]
        return self._columns

    def to_tuples(self) -> T.List[T.Tuple]:
        return [
            tuple(getattr(row, column) for column in self.columns) for row in self.rows
        ]

    def to_dicts(self) -> T.List[T.Dict[str, T.Any]]:
        return [dataclasses.asdict(row) for row in self.rows]
