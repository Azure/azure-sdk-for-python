# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from datetime import date, timedelta, time, datetime
from enum import Enum
import json

from azure.core.serialization import ComplexEncoder, NULL
import isodate
import pytest


def _expand_value(obj):
    try:
        try:
            return obj.to_dict()

        except AttributeError:
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, list):
                return [_expand_value(item) for item in obj]
            elif isinstance(obj, dict):
                return _expand_dict(obj)
            else:
                return _expand_dict(vars(obj))

    except TypeError:
        return obj


def _expand_dict(d):
    return dict((key, _expand_value(value)) for key, value in d.items())


class SerializerMixin(object):
    """Mixin that provides methods for representing a model as a dictionary"""

    def to_dict(self):
        return _expand_value(vars(self))


def test_NULL_is_falsy():
    assert NULL is not False
    assert bool(NULL) is False
    assert NULL is NULL

@pytest.fixture
def json_dumps_with_encoder():
    def func(obj):
        return json.dumps(obj, cls=ComplexEncoder)
    return func

def test_bytes(json_dumps_with_encoder):
    test_bytes = b"mybytes"
    result = json.loads(json_dumps_with_encoder(test_bytes))
    try:
        assert base64.b64decode(result) == test_bytes  # Python 3
    except TypeError:
        assert result == test_bytes  # Python 2.7

def test_byte_array_ascii(json_dumps_with_encoder):
    test_byte_array = bytearray("mybytes", "ascii")
    result = json.loads(json_dumps_with_encoder(test_byte_array))
    assert base64.b64decode(result) == test_byte_array

def test_byte_array_utf8(json_dumps_with_encoder):
    test_byte_array = bytearray("mybytes", "utf-8")
    result = json.loads(json_dumps_with_encoder(test_byte_array))
    assert base64.b64decode(result) == test_byte_array

def test_byte_array_utf16(json_dumps_with_encoder):
    test_byte_array = bytearray("mybytes", "utf-16")
    result = json.loads(json_dumps_with_encoder(test_byte_array))
    assert base64.b64decode(result) == test_byte_array

def test_dictionary_basic(json_dumps_with_encoder):
    test_obj = {
        "string": "myid",
        "number": 42,
        "boolean": True,
        "list_of_string": [1, 2, 3],
        "dictionary_of_number": {"pi": 3.14},
    }
    complex_serialized = json_dumps_with_encoder(test_obj)
    assert json.dumps(test_obj) == complex_serialized
    assert json.loads(complex_serialized) == test_obj

def test_model_basic(json_dumps_with_encoder):
    class BasicModel(SerializerMixin):
        def __init__(self):
            self.string = "myid"
            self.number = 42
            self.boolean = True
            self.list_of_ints = [1, 2, 3]
            self.dictionary_of_number = {"pi": 3.14}

    expected = BasicModel()
    expected_dict = {
        "string": "myid",
        "number": 42,
        "boolean": True,
        "list_of_ints": [1, 2, 3],
        "dictionary_of_number": {"pi": 3.14},
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict

def test_dictionary_datetime(json_dumps_with_encoder):
    test_obj = {
        "timedelta": timedelta(1),
        "date": date(2021, 5, 12),
        "datetime": isodate.parse_datetime('2012-02-24T00:53:52.780Z'),
        "time": time(11,12,13),
    }
    expected = {
        "timedelta": "P1DT00H00M00S",
        "date": "2021-05-12",
        "datetime": '2012-02-24T00:53:52.780000+00:00',
        'time': '11:12:13',
    }
    assert json.loads(json_dumps_with_encoder(test_obj)) == expected

def test_model_datetime(json_dumps_with_encoder):
    class DatetimeModel(SerializerMixin):
        def __init__(self):
            self.timedelta = timedelta(1)
            self.date = date(2021, 5, 12)
            self.datetime = isodate.parse_datetime('2012-02-24T00:53:52.780Z')
            self.time = time(11,12,13)

    expected = DatetimeModel()
    expected_dict = {
        "timedelta": "P1DT00H00M00S",
        "date": "2021-05-12",
        "datetime": '2012-02-24T00:53:52.780000+00:00',
        'time': '11:12:13',
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict

def test_serialize_datetime(json_dumps_with_encoder):

    date_obj = isodate.parse_datetime('2015-01-01T00:00:00')
    date_str = json_dumps_with_encoder(date_obj)

    assert date_str == '"2015-01-01T00:00:00+00:00"'

    date_obj = isodate.parse_datetime('1999-12-31T23:59:59-12:00')
    date_str = json_dumps_with_encoder(date_obj)

    assert date_str == '"2000-01-01T11:59:59+00:00"'

    date_obj = isodate.parse_datetime("2015-06-01T16:10:08.0121-07:00")
    date_str = json_dumps_with_encoder(date_obj)

    assert date_str == '"2015-06-01T23:10:08.012100+00:00"'

    date_obj = datetime.min
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"0001-01-01T00:00:00+00:00"'

    date_obj = datetime.max
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"9999-12-31T23:59:59.999999+00:00"'

    date_obj = isodate.parse_datetime('2012-02-24T00:53:52.000001Z')
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"2012-02-24T00:53:52.000001+00:00"'

    date_obj = isodate.parse_datetime('2012-02-24T00:53:52.780Z')
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"2012-02-24T00:53:52.780000+00:00"'

def test_serialize_time(json_dumps_with_encoder):

    time_str = json_dumps_with_encoder(time(11,22,33))
    assert time_str == '"11:22:33"'

    time_str = json_dumps_with_encoder(time(11,22,33,444444))
    assert time_str == '"11:22:33.444444"'

class BasicEnum(Enum):
    val = "Basic"

class StringEnum(str, Enum):
    val = "string"

class IntEnum(int, Enum):
    val = 1

class FloatEnum(float, Enum):
    val = 1.5

def test_dictionary_enum(json_dumps_with_encoder):
    test_obj = {
        "basic": BasicEnum.val
    }
    with pytest.raises(TypeError):
        json_dumps_with_encoder(test_obj)

    test_obj = {
        "basic": BasicEnum.val.value,
        "string": StringEnum.val.value,
        "int": IntEnum.val.value,
        "float": FloatEnum.val.value
    }
    expected = {
        "basic": "Basic",
        "string": "string",
        "int": 1,
        "float": 1.5
    }
    serialized = json_dumps_with_encoder(test_obj)
    assert json.dumps(test_obj) == serialized
    assert json.loads(serialized) == expected

def test_model_enum(json_dumps_with_encoder):
    class BasicEnumModel:
        def __init__(self):
            self.basic = BasicEnum.val

    with pytest.raises(TypeError):
        json_dumps_with_encoder(BasicEnumModel())

    class EnumModel(SerializerMixin):
        def __init__(self):
            self.basic = BasicEnum.val.value
            self.string = StringEnum.val
            self.int = IntEnum.val
            self.float = FloatEnum.val

    expected = EnumModel()
    expected_dict = {
        "basic": "Basic",
        "string": "string",
        "int": 1,
        "float": 1.5
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict

def test_dictionary_none(json_dumps_with_encoder):
    assert json_dumps_with_encoder(None) == json.dumps(None)
    test_obj = {
        "entry": None
    }
    assert json.loads(json_dumps_with_encoder(test_obj)) == test_obj

def test_model_none(json_dumps_with_encoder):
    class NoneModel(SerializerMixin):
        def __init__(self):
            self.entry = None

    expected = NoneModel()
    expected_dict = {"entry": None}
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict

def test_dictionary_empty_collections(json_dumps_with_encoder):
    test_obj = {
        "dictionary": {},
        "list": [],
        # "tuple": (),  json represents tuples as lists, so this won't round-trip with json.loads
        # "set": set(),  json can't serialize sets. should we?
    }

    assert json.dumps(test_obj) == json_dumps_with_encoder(test_obj)
    assert json.loads(json_dumps_with_encoder(test_obj)) == test_obj

def test_model_empty_collections(json_dumps_with_encoder):
    class EmptyCollectionsModel(SerializerMixin):
        def __init__(self):
            self.dictionary = {}
            self.list = []
            # self.tuple = (),  json represents tuples as lists, so this won't round-trip with json.loads
            # self.set = set(),  json can't serialize sets. should we?

    expected = EmptyCollectionsModel()
    expected_dict = {
        "dictionary": {},
        "list": [],
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict

def test_model_inheritance(json_dumps_with_encoder):
    class ParentModel(SerializerMixin):
        def __init__(self):
            self.parent = "parent"

    class ChildModel(ParentModel):
        def __init__(self):
            super(ChildModel, self).__init__()
            self.child = "child"

    expected = ChildModel()
    expected_dict = {
        "parent": "parent",
        "child": "child",
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict

def test_model_recursion(json_dumps_with_encoder):
    class RecursiveModel(SerializerMixin):
        def __init__(self):
            self.name = "it's me!"
            self.list_of_me = None
            self.dict_of_me = None
            self.dict_of_list_of_me = None
            self.list_of_dict_of_me = None

    expected = RecursiveModel()
    expected.list_of_me = [RecursiveModel()]
    expected.dict_of_me = {"me": RecursiveModel()}
    expected.dict_of_list_of_me = {"many mes": [RecursiveModel()]}
    expected.list_of_dict_of_me = [{"me": RecursiveModel()}]
    expected_dict = {
        "name": "it's me!",
        "list_of_me": [
            {
                "name": "it's me!",
                "list_of_me": None,
                "dict_of_me": None,
                "dict_of_list_of_me": None,
                "list_of_dict_of_me": None
            }
        ],
        "dict_of_me": {
            "me": {
                "name": "it's me!",
                "list_of_me": None,
                "dict_of_me": None,
                "dict_of_list_of_me": None,
                "list_of_dict_of_me": None
            }
        },
        "dict_of_list_of_me": {
            "many mes": [
                {
                    "name": "it's me!",
                    "list_of_me": None,
                    "dict_of_me": None,
                    "dict_of_list_of_me": None,
                    "list_of_dict_of_me": None
                }
            ]
        },
        "list_of_dict_of_me": [
            {"me": {
                    "name": "it's me!",
                    "list_of_me": None,
                    "dict_of_me": None,
                    "dict_of_list_of_me": None,
                    "list_of_dict_of_me": None
                }
            }
        ]
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict
