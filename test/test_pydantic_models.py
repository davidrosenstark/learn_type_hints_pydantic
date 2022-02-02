from datetime import datetime
from typing import List, Optional

import dateparser
import pytest
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError


class User(BaseModel):
    id: int
    name = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: List[int] = []


data = {
    'id': '123',
    'signup_ts': '2019-06-01 12:22',
    'friends': [1, 2, '3'],
}


def test_valid_data():
    """Test where we see casting of data done automatically"""
    user = User(**data)
    data['signup_ts'] = dateparser.parse(data['signup_ts'])
    data['friends'] = [int(i) for i in data['friends']]
    data['id'] = int(data['id'])
    data['name'] = 'John Doe'
    assert user.dict() == data


def test_missing_param():
    bad_data = {
        'signup_ts': '2019-06-01 12:22',
        'friends': [1, 2, '3']
    }
    with pytest.raises(ValidationError) as ex:
        User(**bad_data)
    assert str(ex.value) == '1 validation error for User\nid\n  field required (type=value_error.missing)'


def test_json_serialize():
    user = User(**data)
    # no import of json
    expected = '{"id": 123, "signup_ts": "2019-06-01T12:22:00", "friends": [1, 2, 3], "name": "John Doe"}'
    assert user.json() == expected
    user1 = User.parse_raw(expected)
    assert user1 == user


def test_json_errors():
    bad = '{"id": "123", "signup_ts": "2019-06-01T12:22:00", "friends": "str", "name": "John Doe"}'
    with pytest.raises(ValidationError) as ex:
        User.parse_raw(bad)
    assert str(ex.value) == '1 validation error for User\nfriends\n  value is not a valid list (type=type_error.list)'


def test_invalid_date():
    bad_data = {
        'id': '123',
        'signup_ts': 'bad',
        'friends': [1, 2, '3'],
    }
    with pytest.raises(ValidationError) as ex:
        User(**bad_data)
    assert str(
        ex.value
    ) == '1 validation error for User\nsignup_ts\n  invalid datetime format (type=value_error.datetime)'


def test_invalid_id_and_ts():
    bad_data = {
        'id': 'string',
        'signup_ts': 'bad',
        'friends': [1, 2, '3'],
    }
    with pytest.raises(ValidationError) as ex:
        User(**bad_data)
    assert str(
        ex.value
    ) == '2 validation errors for User\nid\n  value is not a valid integer (type=type_error.integer)\n' \
         'signup_ts\n  invalid datetime format (type=value_error.datetime)'

