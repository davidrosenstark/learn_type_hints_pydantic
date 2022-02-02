from datetime import datetime
from typing import Annotated
from typing import get_type_hints
import pytest

seconds = Annotated[int, "seconds"]
millis = Annotated[int, "millis"]


def get_date_sec(ts: seconds) -> datetime:
    return datetime.fromtimestamp(ts)


def get_date_ms(ts: millis) -> datetime:
    return datetime.fromtimestamp(ts / 1000)


def test_seconds():
    ts = 1643205440
    actual = get_date_sec(ts)
    assert actual.timestamp() == ts


def test_millis():
    ts = 1643205440329
    actual = get_date_ms(ts)
    assert actual.timestamp() == ts / 1000


def test_type_hints():
    ts = 1643205440329
    with pytest.raises(TypeError) as ex:
        get_type_hints(ts, include_extras=True)


def func(s: str):
    print(s)


def test_incorrect_type():
    func(123)
    assert True
