# -*- coding: utf-8 -*-

import dataclasses
from fixa.dataclass_dataframe import TypedDataFrame


@dataclasses.dataclass
class User:
    id: int
    name: str


@dataclasses.dataclass
class UserDataFrame(TypedDataFrame[User]):
    row_type = User


class TestTypedDataFrame:
    def test(self):
        df = UserDataFrame(rows=[User(id=1, name="a"), User(id=2, name="b")])
        assert df.columns == ["id", "name"]
        assert df.to_tuples() == [(1, "a"), (2, "b")]
        assert df.to_dicts() == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.dataclass_dataframe", preview=False)
