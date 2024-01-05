# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from fixa.better_dataclasses import (
    DataClass,
)

verbose = False


@dataclasses.dataclass
class Data(DataClass):
    value: int = dataclasses.field()

    def special_data_method(self):
        if verbose:
            print("call special_data_method")


@dataclasses.dataclass
class Profile(DataClass):
    """
    firstname, lastname, ssn are generic data type field.
    """

    firstname: str = dataclasses.field()
    lastname: str = dataclasses.field()
    ssn: str = dataclasses.field()

    def special_profile_method(self):
        if verbose:
            print("call special_profile_method")


@dataclasses.dataclass
class Degree(DataClass):
    name: str = dataclasses.field()
    year: int = dataclasses.field()

    def special_degree_method(self):
        if verbose:
            print("call special_degree_method")


@dataclasses.dataclass
class People(DataClass):
    """
    - ``profile`` is nested field.
    - ``degrees`` is collection type field.
    """

    # fmt: off
    id: int = dataclasses.field()
    profile: T.Optional[Profile] = Profile.nested_field(default=None)
    degrees: T.Optional[T.List[Degree]] = Degree.list_of_nested_field(default_factory=list)
    # fmt: on

    def special_people_method(self):
        if verbose:
            print("call special_people_method")


def test_from_dict_and_from_list():
    data = Data.from_dict({"value": 1})
    assert isinstance(data, Data)
    data.special_data_method()  # type hint OK

    data = Data.from_dict(Data(value=1))
    assert isinstance(data, Data)
    data.special_data_method()  # type hint OK

    data = Data.from_dict(None)
    assert data is None

    data_list = Data.from_list([{"value": 1}])
    assert isinstance(data_list[0], Data)
    data_list.copy()  # type hint OK
    data_list[0].special_data_method()  # type hint OK

    data_list = Data.from_list([Data(value=1)])
    assert isinstance(data_list[0], Data)
    data_list.copy()  # type hint OK
    data_list[0].special_data_method()  # type hint OK

    data_list = Data.from_list([None])
    assert data_list == [None]
    data_list.copy()  # type hint OK

    data_list = Data.from_list([{"value": 1}, Data(value=1), None])
    data_list[0].special_data_method()  # type hint OK
    data_list[1].special_data_method()  # type hint OK


def test_nested_1():
    """
    Deserialize from nested dictionary data
    """
    people = People(
        id=1,
        profile=Profile(
            firstname="David",
            lastname="John",
            ssn="123-45-6789",
        ),
        degrees=[
            Degree(name="Bachelor", year=2004),
            Degree(name="Master", year=2006),
        ],
    )
    people_data = people.to_dict()
    people1 = People.from_dict(people_data)
    people1_data = people1.to_dict()
    assert people == people1
    assert people_data == people1_data

    # test type hint
    _ = people1.special_people_method()  # type hint OK

    degree = Degree.from_dict({"name": "", "year": 1990})
    _ = degree.special_degree_method()  # type hint OK

    degree_list = Degree.from_list(
        [{"name": "", "year": 1990}, {"name": "", "year": 2000}]
    )
    degree = degree_list[0]
    _ = degree.special_degree_method()  # type hint OK


def test_nested_2():
    """
    nested value is None.
    """
    people = People(
        id=1,
        profile=None,
        degrees=None,
    )
    people_data = people.to_dict()
    people1 = People.from_dict(people_data)
    people1_data = people1.to_dict()
    assert people == people1
    assert people_data == people1_data


def test_profile_degrees_default_value():
    people = People(id=1)
    assert people.profile is None
    assert people.degrees == list()

    people_data = people.to_dict()
    people1 = People.from_dict(people_data)
    assert people == people1
    assert people1.profile is None
    assert people1.degrees == list()


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.better_dataclasses", preview=False)
