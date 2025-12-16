# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from datetime import date, datetime, time, timedelta, tzinfo
from enum import Enum
import json
import sys
import typing
from typing import Any, Dict, List, Optional, Union, Type
from io import BytesIO

from azure.core.serialization import (
    AzureJSONEncoder,
    NULL,
    as_attribute_dict,
    get_backcompat_attr_name,
    is_generated_model,
    attribute_list,
)
from azure.core.exceptions import DeserializationError
import pytest
from modeltypes._utils.model_base import (
    Model as HybridModel,
    SdkJSONEncoder,
    rest_field,
    TYPE_HANDLER_REGISTRY,
    _deserialize,
)
from modeltypes._utils.serialization import Model as MsrestModel
from modeltypes import models


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


class DatetimeSubclass(datetime):
    """datetime.datetime subclass that tests datetimes without a type() of datetime.datetime"""


class SerializerMixin(object):
    """Mixin that provides methods for representing a model as a dictionary"""

    def to_dict(self):
        return _expand_value(vars(self))


class NegativeUtcOffset(tzinfo):
    """tzinfo class with UTC offset of -12 hours"""

    _offset = timedelta(seconds=-43200)
    _dst = timedelta(0)
    _name = "-1200"

    def utcoffset(self, dt):
        return self.__class__._offset

    def dst(self, dt):
        return self.__class__._dst

    def tzname(self, dt):
        return self.__class__._name


class PositiveUtcOffset(tzinfo):
    """tzinfo class with UTC offset of +12 hours"""

    _offset = timedelta(seconds=43200)
    _dst = timedelta(0)
    _name = "+1200"

    def utcoffset(self, dt):
        return self.__class__._offset

    def dst(self, dt):
        return self.__class__._dst

    def tzname(self, dt):
        return self.__class__._name


def test_NULL_is_falsy():
    assert NULL is not False
    assert bool(NULL) is False
    assert NULL is NULL


@pytest.fixture
def json_dumps_with_encoder():
    def func(obj):
        return json.dumps(obj, cls=AzureJSONEncoder)

    return func


def test_bytes(json_dumps_with_encoder):
    test_bytes = b"mybytes"
    result = json.loads(json_dumps_with_encoder(test_bytes))
    assert base64.b64decode(result) == test_bytes


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


def test_dictionary_set():
    """Test that dictionary mutations via attribute syntax persist and sync to dictionary syntax."""

    class MyModel(HybridModel):
        my_dict: Dict[str, int] = rest_field(visibility=["read", "create", "update", "delete", "query"])

    # Test 1: Basic mutation via attribute syntax
    m = MyModel(my_dict={"a": 1, "b": 2})
    assert m.my_dict == {"a": 1, "b": 2}

    # Test 2: Add new key via attribute syntax and verify it persists
    m.my_dict["c"] = 3
    assert m.my_dict["c"] == 3
    assert m.my_dict == {"a": 1, "b": 2, "c": 3}

    # Test 3: Verify mutation is reflected in dictionary syntax
    assert m["my_dict"] == {"a": 1, "b": 2, "c": 3}

    # Test 4: Modify existing key via attribute syntax
    m.my_dict["a"] = 100
    assert m.my_dict["a"] == 100
    assert m["my_dict"]["a"] == 100

    # Test 5: Delete key via attribute syntax
    del m.my_dict["b"]
    assert "b" not in m.my_dict
    assert "b" not in m["my_dict"]

    # Test 6: Update via dict methods
    m.my_dict.update({"d": 4, "e": 5})
    assert m.my_dict["d"] == 4
    assert m.my_dict["e"] == 5
    assert m["my_dict"]["d"] == 4

    # Test 7: Clear via attribute syntax and verify via dictionary syntax
    m.my_dict.clear()
    assert len(m.my_dict) == 0
    assert len(m["my_dict"]) == 0

    # Test 8: Reassign entire dictionary via attribute syntax
    m.my_dict = {"x": 10, "y": 20}
    assert m.my_dict == {"x": 10, "y": 20}
    assert m["my_dict"] == {"x": 10, "y": 20}

    # Test 9: Mutation after reassignment
    m.my_dict["z"] = 30
    assert m.my_dict["z"] == 30
    assert m["my_dict"]["z"] == 30

    # Test 10: Access via dictionary syntax first, then mutate via attribute syntax
    m.my_dict["w"] = 40
    assert m["my_dict"]["w"] == 40

    # Test 11: Multiple accesses maintain same cached object
    dict_ref1 = m.my_dict
    dict_ref2 = m.my_dict
    assert dict_ref1 is dict_ref2
    dict_ref1["new_key"] = 999
    assert dict_ref2["new_key"] == 999
    assert m.my_dict["new_key"] == 999


def test_list_set():
    """Test that list mutations via attribute syntax persist and sync to dictionary syntax."""

    class MyModel(HybridModel):
        my_list: List[int] = rest_field(visibility=["read", "create", "update", "delete", "query"])

    # Test 1: Basic mutation via attribute syntax
    m = MyModel(my_list=[1, 2, 3])
    assert m.my_list == [1, 2, 3]

    # Test 2: Append via attribute syntax and verify it persists
    m.my_list.append(4)
    assert m.my_list == [1, 2, 3, 4]

    # Test 3: Verify mutation is reflected in dictionary syntax
    assert m["my_list"] == [1, 2, 3, 4]

    # Test 4: Modify existing element via attribute syntax
    m.my_list[0] = 100
    assert m.my_list[0] == 100
    assert m["my_list"][0] == 100

    # Test 5: Extend list via attribute syntax
    m.my_list.extend([5, 6])
    assert m.my_list == [100, 2, 3, 4, 5, 6]
    assert m["my_list"] == [100, 2, 3, 4, 5, 6]

    # Test 6: Remove element via attribute syntax
    m.my_list.remove(2)
    assert 2 not in m.my_list
    assert 2 not in m["my_list"]

    # Test 7: Pop element
    popped = m.my_list.pop()
    assert popped == 6
    assert 6 not in m.my_list
    assert 6 not in m["my_list"]

    # Test 8: Insert element
    m.my_list.insert(0, 999)
    assert m.my_list[0] == 999
    assert m["my_list"][0] == 999

    # Test 9: Clear via attribute syntax
    m.my_list.clear()
    assert len(m.my_list) == 0
    assert len(m["my_list"]) == 0

    # Test 10: Reassign entire list via attribute syntax
    m.my_list = [10, 20, 30]
    assert m.my_list == [10, 20, 30]
    assert m["my_list"] == [10, 20, 30]

    # Test 11: Mutation after reassignment
    m.my_list.append(40)
    assert m.my_list == [10, 20, 30, 40]
    assert m["my_list"] == [10, 20, 30, 40]

    # Test 12: Multiple accesses maintain same cached object
    list_ref1 = m.my_list
    list_ref2 = m.my_list
    assert list_ref1 is list_ref2
    list_ref1.append(50)
    assert 50 in list_ref2
    assert 50 in m.my_list


def test_set_collection():
    """Test that set mutations via attribute syntax persist and sync to dictionary syntax."""

    class MyModel(HybridModel):
        my_set: typing.Set[int] = rest_field(visibility=["read", "create", "update", "delete", "query"])

    # Test 1: Basic mutation via attribute syntax
    m = MyModel(my_set={1, 2, 3})
    assert m.my_set == {1, 2, 3}

    # Test 2: Add via attribute syntax and verify it persists
    m.my_set.add(4)
    assert 4 in m.my_set

    # Test 3: Verify mutation is reflected in dictionary syntax
    assert 4 in m["my_set"]

    # Test 4: Remove element via attribute syntax
    m.my_set.remove(2)
    assert 2 not in m.my_set
    assert 2 not in m["my_set"]

    # Test 5: Update set via attribute syntax
    m.my_set.update({5, 6, 7})
    assert m.my_set == {1, 3, 4, 5, 6, 7}
    assert m["my_set"] == {1, 3, 4, 5, 6, 7}

    # Test 6: Discard element
    m.my_set.discard(1)
    assert 1 not in m.my_set
    assert 1 not in m["my_set"]

    # Test 7: Clear via attribute syntax
    m.my_set.clear()
    assert len(m.my_set) == 0
    assert len(m["my_set"]) == 0

    # Test 8: Reassign entire set via attribute syntax
    m.my_set = {10, 20, 30}
    assert m.my_set == {10, 20, 30}
    assert m["my_set"] == {10, 20, 30}

    # Test 9: Mutation after reassignment
    m.my_set.add(40)
    assert 40 in m.my_set
    assert 40 in m["my_set"]

    # Test 10: Multiple accesses maintain same cached object
    set_ref1 = m.my_set
    set_ref2 = m.my_set
    assert set_ref1 is set_ref2
    set_ref1.add(50)
    assert 50 in set_ref2
    assert 50 in m.my_set


def test_dictionary_set_datetime():
    """Test that dictionary with datetime values properly serializes/deserializes."""
    from datetime import datetime, timezone

    class MyModel(HybridModel):
        my_dict: Dict[str, datetime] = rest_field(visibility=["read", "create", "update", "delete", "query"])

    # Test 1: Initialize with datetime values
    dt1 = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    dt2 = datetime(2023, 6, 20, 14, 15, 30, tzinfo=timezone.utc)
    m = MyModel(my_dict={"created": dt1, "updated": dt2})

    # Test 2: Access via attribute syntax returns datetime objects
    assert isinstance(m.my_dict["created"], datetime)
    assert isinstance(m.my_dict["updated"], datetime)
    assert m.my_dict["created"] == dt1
    assert m.my_dict["updated"] == dt2

    # Test 3: Access via dictionary syntax returns serialized strings (ISO format)
    dict_access = m["my_dict"]
    assert isinstance(dict_access["created"], str)
    assert isinstance(dict_access["updated"], str)
    assert dict_access["created"] == "2023-01-15T10:30:45Z"
    assert dict_access["updated"] == "2023-06-20T14:15:30Z"

    # Test 4: Mutate via attribute syntax with new datetime
    dt3 = datetime(2023, 12, 25, 18, 0, 0, tzinfo=timezone.utc)
    m.my_dict["holiday"] = dt3
    assert m.my_dict["holiday"] == dt3

    # Test 5: Verify mutation is serialized in dictionary syntax
    assert m["my_dict"]["holiday"] == "2023-12-25T18:00:00Z"

    # Test 6: Update existing datetime via attribute syntax
    dt4 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    m.my_dict["created"] = dt4
    assert m.my_dict["created"] == dt4
    assert m["my_dict"]["created"] == "2024-01-01T00:00:00Z"

    # Test 7: Verify all datetimes are deserialized correctly after mutation
    assert isinstance(m.my_dict["created"], datetime)
    assert isinstance(m.my_dict["updated"], datetime)
    assert isinstance(m.my_dict["holiday"], datetime)

    # Test 8: Use dict update method with datetimes
    dt5 = datetime(2024, 6, 15, 12, 30, 0, tzinfo=timezone.utc)
    dt6 = datetime(2024, 7, 4, 16, 45, 0, tzinfo=timezone.utc)
    m.my_dict.update({"event1": dt5, "event2": dt6})
    assert m.my_dict["event1"] == dt5
    assert m["my_dict"]["event1"] == "2024-06-15T12:30:00Z"

    # Test 9: Reassign entire dictionary with new datetimes
    dt7 = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    dt8 = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    m.my_dict = {"start": dt7, "end": dt8}
    assert m.my_dict["start"] == dt7
    assert m.my_dict["end"] == dt8
    assert m["my_dict"]["start"] == "2025-01-01T00:00:00Z"
    assert m["my_dict"]["end"] == "2025-12-31T23:59:59Z"

    # Test 10: Cached object maintains datetime type
    dict_ref1 = m.my_dict
    dict_ref2 = m.my_dict
    assert dict_ref1 is dict_ref2
    assert isinstance(dict_ref1["start"], datetime)
    assert isinstance(dict_ref2["start"], datetime)


def test_model_basic(json_dumps_with_encoder):
    class BasicModel(SerializerMixin):
        def __init__(self):
            self.string = "myid"
            self.number = 42
            self.boolean = True
            self.list_of_ints = [1, 2, 3]
            self.dictionary_of_number = {"pi": 3.14}
            self.bytes_data = b"data as bytes"

    expected = BasicModel()
    expected_bytes = "data as bytes" if sys.version_info.major == 2 else "ZGF0YSBhcyBieXRlcw=="  # cspell:disable-line
    expected_dict = {
        "string": "myid",
        "number": 42,
        "boolean": True,
        "list_of_ints": [1, 2, 3],
        "dictionary_of_number": {"pi": 3.14},
        "bytes_data": expected_bytes,
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict


def test_dictionary_datetime(json_dumps_with_encoder):
    test_obj = {
        "timedelta": timedelta(1),
        "date": date(2021, 5, 12),
        "datetime": datetime.strptime("2012-02-24T00:53:52.780Z", "%Y-%m-%dT%H:%M:%S.%fZ"),
        "time": time(11, 12, 13),
    }
    expected = {
        "timedelta": "P1DT00H00M00S",
        "date": "2021-05-12",
        "datetime": "2012-02-24T00:53:52.780000Z",
        "time": "11:12:13",
    }
    assert json.loads(json_dumps_with_encoder(test_obj)) == expected


def test_model_datetime(json_dumps_with_encoder):
    class DatetimeModel(SerializerMixin):
        def __init__(self):
            self.timedelta = timedelta(1)
            self.date = date(2021, 5, 12)
            self.datetime = datetime.strptime("2012-02-24T00:53:52.780Z", "%Y-%m-%dT%H:%M:%S.%fZ")
            self.time = time(11, 12, 13)

    expected = DatetimeModel()
    expected_dict = {
        "timedelta": "P1DT00H00M00S",
        "date": "2021-05-12",
        "datetime": "2012-02-24T00:53:52.780000Z",
        "time": "11:12:13",
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict


def test_model_key_vault(json_dumps_with_encoder):
    class Attributes(SerializerMixin):
        def __init__(self):
            self.enabled = True
            self.not_before = datetime.strptime("2012-02-24T00:53:52.780Z", "%Y-%m-%dT%H:%M:%S.%fZ")
            self.expires = datetime.strptime("2032-02-24T00:53:52.780Z", "%Y-%m-%dT%H:%M:%S.%fZ")
            self.created = datetime.strptime("2020-02-24T00:53:52.780Z", "%Y-%m-%dT%H:%M:%S.%fZ")
            self.updated = datetime.strptime("2021-02-24T00:53:52.780Z", "%Y-%m-%dT%H:%M:%S.%fZ")

    class ResourceId(SerializerMixin):
        def __init__(self):
            self.source_id = "source-id"
            self.vault_url = "vault-url"
            self.name = "name"
            self.version = None

    class Identifier(SerializerMixin):
        def __init__(self):
            self._resource_id = ResourceId()

    class Properties(SerializerMixin):
        def __init__(self):
            self._attributes = Attributes()
            self._id = "id"
            self._vault_id = Identifier()
            self._thumbprint = b"thumbprint bytes"
            self._tags = None

    expected = Properties()
    expected_bytes = (
        "thumbprint bytes" if sys.version_info.major == 2 else "dGh1bWJwcmludCBieXRlcw=="
    )  # cspell:disable-line
    expected_dict = {
        "_attributes": {
            "enabled": True,
            "not_before": "2012-02-24T00:53:52.780000Z",
            "expires": "2032-02-24T00:53:52.780000Z",
            "created": "2020-02-24T00:53:52.780000Z",
            "updated": "2021-02-24T00:53:52.780000Z",
        },
        "_id": "id",
        "_vault_id": {
            "_resource_id": {
                "source_id": "source-id",
                "vault_url": "vault-url",
                "name": "name",
                "version": None,
            },
        },
        "_thumbprint": expected_bytes,
        "_tags": None,
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict


def test_serialize_datetime(json_dumps_with_encoder):

    date_obj = datetime.strptime("2015-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
    date_str = json_dumps_with_encoder(date_obj)

    assert date_str == '"2015-01-01T00:00:00Z"'

    date_obj = datetime.strptime("1999-12-31T23:59:59", "%Y-%m-%dT%H:%M:%S").replace(tzinfo=NegativeUtcOffset())
    date_str = json_dumps_with_encoder(date_obj)

    assert date_str == '"2000-01-01T11:59:59Z"'

    date_obj = datetime.strptime("2015-06-01T16:10:08.0121", "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=PositiveUtcOffset())
    date_str = json_dumps_with_encoder(date_obj)

    assert date_str == '"2015-06-01T04:10:08.012100Z"'

    date_obj = datetime.min
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"0001-01-01T00:00:00Z"'

    date_obj = datetime.max
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"9999-12-31T23:59:59.999999Z"'

    date_obj = datetime.strptime("2012-02-24T00:53:52.000001Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"2012-02-24T00:53:52.000001Z"'

    date_obj = datetime.strptime("2012-02-24T00:53:52.780Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"2012-02-24T00:53:52.780000Z"'


def test_serialize_datetime_subclass(json_dumps_with_encoder):

    date_obj = DatetimeSubclass.strptime("2012-02-24T00:53:52.780Z", "%Y-%m-%dT%H:%M:%S.%fZ")
    date_str = json_dumps_with_encoder(date_obj)
    assert date_str == '"2012-02-24T00:53:52.780000Z"'


def test_serialize_time(json_dumps_with_encoder):

    time_str = json_dumps_with_encoder(time(11, 22, 33))
    assert time_str == '"11:22:33"'

    time_str = json_dumps_with_encoder(time(11, 22, 33, 444444))
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
    test_obj = {"basic": BasicEnum.val}
    with pytest.raises(TypeError):
        json_dumps_with_encoder(test_obj)

    test_obj = {
        "basic": BasicEnum.val.value,
        "string": StringEnum.val.value,
        "int": IntEnum.val.value,
        "float": FloatEnum.val.value,
    }
    expected = {"basic": "Basic", "string": "string", "int": 1, "float": 1.5}
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
    expected_dict = {"basic": "Basic", "string": "string", "int": 1, "float": 1.5}
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict


def test_dictionary_none(json_dumps_with_encoder):
    assert json_dumps_with_encoder(None) == json.dumps(None)
    test_obj = {"entry": None}
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
    }

    assert json.dumps(test_obj) == json_dumps_with_encoder(test_obj)
    assert json.loads(json_dumps_with_encoder(test_obj)) == test_obj


def test_model_empty_collections(json_dumps_with_encoder):
    class EmptyCollectionsModel(SerializerMixin):
        def __init__(self):
            self.dictionary = {}
            self.list = []

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
                "list_of_dict_of_me": None,
            }
        ],
        "dict_of_me": {
            "me": {
                "name": "it's me!",
                "list_of_me": None,
                "dict_of_me": None,
                "dict_of_list_of_me": None,
                "list_of_dict_of_me": None,
            }
        },
        "dict_of_list_of_me": {
            "many mes": [
                {
                    "name": "it's me!",
                    "list_of_me": None,
                    "dict_of_me": None,
                    "dict_of_list_of_me": None,
                    "list_of_dict_of_me": None,
                }
            ]
        },
        "list_of_dict_of_me": [
            {
                "me": {
                    "name": "it's me!",
                    "list_of_me": None,
                    "dict_of_me": None,
                    "dict_of_list_of_me": None,
                    "list_of_dict_of_me": None,
                }
            }
        ],
    }
    assert json.loads(json_dumps_with_encoder(expected.to_dict())) == expected_dict


def test_json_roundtrip():
    dict_response = {
        "name": "wall-e",
        "species": "dog",
    }
    model = models.HybridPet(
        name="wall-e",
        species="dog",
    )
    with pytest.raises(TypeError):
        json.dumps(model)
    assert json.dumps(dict(model)) == '{"name": "wall-e", "species": "dog"}'
    assert json.loads(json.dumps(dict(model))) == model == dict_response


def test_flattened_model():
    def _test(result):
        assert result["name"] == "wall-e"
        assert result["description"] == "a dog"
        assert result["age"] == 2
        assert "properties" not in result
        assert "modelDescription" not in result
        assert "model_description" not in result

    model = models.FlattenModel(name="wall-e", description="a dog", age=2)
    _test(as_attribute_dict(model))
    model = models.FlattenModel({"name": "wall-e", "properties": {"modelDescription": "a dog", "age": 2}})
    _test(as_attribute_dict(model))


def test_client_name_model():
    model = models.ClientNameAndJsonEncodedNameModel(client_name="wall-e")
    assert model.client_name == "wall-e"
    assert model["wireName"] == "wall-e"

    model = models.ClientNameAndJsonEncodedNameModel({"wireName": "wall-e"})
    assert model.client_name == "wall-e"
    assert model["wireName"] == "wall-e"


def test_readonly():
    model = models.ReadonlyModel({"id": 1})
    assert model.id == 1
    assert model.as_dict() == {"id": 1}
    assert model.as_dict(exclude_readonly=True) == {}


def test_as_attribute_dict_scratch():
    model = models.Scratch(prop="test")
    assert as_attribute_dict(model) == {"prop": "test"}


def test_is_generated_model_with_hybrid_model():
    assert is_generated_model(HybridModel())
    assert is_generated_model(models.FlattenModel({"name": "wall-e", "properties": {"description": "a dog", "age": 2}}))
    assert is_generated_model(models.ClientNameAndJsonEncodedNameModel(client_name="wall-e"))
    assert is_generated_model(models.ReadonlyModel())


def test_is_generated_model_with_msrest_model():
    assert is_generated_model(models.MsrestPet(name="wall-e", species="dog"))


def test_is_generated_model_with_non_models():
    assert not is_generated_model({})
    assert not is_generated_model([])
    assert not is_generated_model("string")
    assert not is_generated_model(42)
    assert not is_generated_model(None)
    assert not is_generated_model(object)

    class Model:
        def __init__(self):
            self.attr = "value"

    assert not is_generated_model(Model())


def test_attribute_list_non_model():
    with pytest.raises(TypeError):
        attribute_list({})

    with pytest.raises(TypeError):
        attribute_list([])

    with pytest.raises(TypeError):
        attribute_list("string")

    with pytest.raises(TypeError):
        attribute_list(42)

    with pytest.raises(TypeError):
        attribute_list(None)

    with pytest.raises(TypeError):
        attribute_list(object)

    class RandomModel:
        def __init__(self):
            self.attr = "value"

    with pytest.raises(TypeError):
        attribute_list(RandomModel())


def test_attribute_list_scratch_model():
    model = models.HybridPet(name="wall-e", species="dog")
    assert attribute_list(model) == ["name", "species"]
    msrest_model = models.MsrestPet(name="wall-e", species="dog")
    assert attribute_list(msrest_model) == ["name", "species"]


def test_attribute_list_client_named_property_model():
    model = models.ClientNameAndJsonEncodedNameModel(client_name="wall-e")
    assert attribute_list(model) == ["client_name"]
    msrest_model = models.MsrestClientNameAndJsonEncodedNameModel(client_name="wall-e")
    assert attribute_list(msrest_model) == ["client_name"]


def test_attribute_list_flattened_model():
    model = models.FlattenModel(name="wall-e", description="a dog", age=2)
    assert attribute_list(model) == ["name", "description", "age"]
    msrest_model = models.MsrestFlattenModel(name="wall-e", description="a dog", age=2)
    assert attribute_list(msrest_model) == ["name", "description", "age"]


def test_attribute_list_readonly_model():
    model = models.ReadonlyModel({"id": 1})
    assert attribute_list(model) == ["id"]
    msrest_model = models.MsrestReadonlyModel(id=1)
    assert attribute_list(msrest_model) == ["id"]


def test_attribute_list_additional_properties_hybrid():
    hybrid_model = models.HybridPetAPTrue(
        {"birthdate": "2017-12-13T02:29:51Z", "complexProperty": {"color": "Red"}, "name": "Buddy"}
    )
    assert attribute_list(hybrid_model) == ["name"]


def test_attribute_list_additional_properties_msrest():
    msrest_model = models.MsrestPetAPTrue(
        additional_properties={"birthdate": "2017-12-13T02:29:51Z", "complexProperty": {"color": "Red"}}, name="Buddy"
    )
    assert attribute_list(msrest_model) == ["additional_properties", "name"]


def test_as_attribute_dict_client_name():
    model = models.ClientNameAndJsonEncodedNameModel(client_name="wall-e")
    assert model.as_dict() == {"wireName": "wall-e"}
    assert as_attribute_dict(model) == {"client_name": "wall-e"}


def test_as_attribute_dict_nested_models():
    def _test(result):
        assert result["name"] == "Jane Doe"
        assert result["home_address"]["street"] == "123 Home St"
        assert result["home_address"]["city"] == "Hometown"
        assert result["home_address"]["zip_code"] == "12345"
        assert result["work_address"]["street"] == "456 Work Ave"
        assert result["work_address"]["city"] == "Workville"
        assert result["work_address"]["zip_code"] == "67890"

    hybrid_home = models.HybridAddress(street="123 Home St", city="Hometown", zip_code="12345")
    hybrid_work = models.HybridAddress(street="456 Work Ave", city="Workville", zip_code="67890")
    hybrid_person = models.HybridPerson(name="Jane Doe", home_address=hybrid_home, work_address=hybrid_work)
    _test(as_attribute_dict(hybrid_person))
    msrest_home = models.MsrestAddress(street="123 Home St", city="Hometown", zip_code="12345")
    msrest_work = models.MsrestAddress(street="456 Work Ave", city="Workville", zip_code="67890")
    msrest_person = models.MsrestPerson(name="Jane Doe", home_address=msrest_home, work_address=msrest_work)
    _test(as_attribute_dict(msrest_person))


def test_as_attribute_dict_wire_name_differences():
    def _test(result):
        assert result["product_id"] == "p123"
        assert result["product_name"] == "Widget"
        assert result["unit_price"] == 19.99
        assert result["stock_count"] == 42

    hybrid_product = models.HybridProduct(product_id="p123", product_name="Widget", unit_price=19.99, stock_count=42)
    assert hybrid_product["productId"] == "p123"
    assert hybrid_product["ProductName"] == "Widget"
    assert hybrid_product["unit-price"] == 19.99
    assert hybrid_product["stock_count"] == 42
    _test(as_attribute_dict(hybrid_product))

    msrest_product = models.MsrestProduct(product_id="p123", product_name="Widget", unit_price=19.99, stock_count=42)
    _test(as_attribute_dict(msrest_product))


def test_as_attribute_dict_datetime_serialization():
    def _test(result):
        assert result["event_id"] == "e789"
        assert isinstance(result["start_time"], str)
        # TODO: chase why there are serialization diffs
        assert result["start_time"] in ["2023-05-15T09:00:00Z", "2023-05-15T09:00:00.000Z"]
        assert result["end_time"] in ["2023-05-15T10:30:00Z", "2023-05-15T10:30:00.000Z"]
        assert result["created_date"] == "2023-05-01"
        assert result["reminder_time"] == "08:45:00"
        assert result["duration"] in ["PT1H30M", "PT01H30M00S"]  # Duration can be represented in different ways

    hybrid_event = models.HybridEvent(
        event_id="e789",
        start_time=datetime(2023, 5, 15, 9, 0, 0),
        end_time=datetime(2023, 5, 15, 10, 30, 0),
        created_date=date(2023, 5, 1),
        reminder_time=time(8, 45, 0),
        duration=timedelta(hours=1, minutes=30),
    )
    _test(as_attribute_dict(hybrid_event))
    msrest_event = models.MsrestEvent(
        event_id="e789",
        start_time=datetime(2023, 5, 15, 9, 0, 0),
        end_time=datetime(2023, 5, 15, 10, 30, 0),
        created_date=date(2023, 5, 1),
        reminder_time=time(8, 45, 0),
        duration=timedelta(hours=1, minutes=30),
    )
    _test(as_attribute_dict(msrest_event))


def test_as_attribute_dict_readonly():
    def _test_all(result):
        assert result["id"] == "r456"
        assert result["name"] == "My Resource"
        assert result["description"] == "A test resource"

    def _test_exclude_readonly(result):
        assert "id" not in result
        assert result["name"] == "My Resource"
        assert result["description"] == "A test resource"

    hybrid_resource = models.HybridResource(id="r456", name="My Resource", description="A test resource")

    # Should include all properties
    _test_all(as_attribute_dict(hybrid_resource))
    # Should exclude readonly properties
    _test_exclude_readonly(as_attribute_dict(hybrid_resource, exclude_readonly=True))

    msrest_resource = models.MsrestResource(name="My Resource", description="A test resource")
    msrest_resource.id = "r456"  # Manually set the readonly property for testing
    # Should include all properties
    _test_all(as_attribute_dict(msrest_resource))
    # Should exclude readonly properties
    _test_exclude_readonly(as_attribute_dict(msrest_resource, exclude_readonly=True))


def test_as_attribute_dict_collections():
    def _test(result):
        assert result["name"] == "Tagged Resource"
        assert len(result["tags"]) == 2
        assert result["tags"][0]["key"] == "env"
        assert result["tags"][0]["value"] == "prod"
        assert result["tags"][1]["key"] == "dept"
        assert result["tags"][1]["value"] == "finance"
        assert result["metadata"]["created_by"] == "admin"
        assert result["metadata"]["priority"] == "high"
        assert result["string_list"] == ["a", "b", "c"]
        assert result["int_list"] == [1, 2, 3]

    hybrid_tags = [models.HybridTag(key="env", value="prod"), models.HybridTag(key="dept", value="finance")]
    hybrid_resource = models.HybridTaggedResource(
        name="Tagged Resource",
        tags=hybrid_tags,
        metadata={"created_by": "admin", "priority": "high"},
        string_list=["a", "b", "c"],
        int_list=[1, 2, 3],
    )
    _test(as_attribute_dict(hybrid_resource))

    msrest_tags = [models.MsrestTag(key="env", value="prod"), models.MsrestTag(key="dept", value="finance")]
    msrest_resource = models.MsrestTaggedResource(
        name="Tagged Resource",
        tags=msrest_tags,
        metadata={"created_by": "admin", "priority": "high"},
        string_list=["a", "b", "c"],
        int_list=[1, 2, 3],
    )
    _test(as_attribute_dict(msrest_resource))


def test_as_attribute_dict_inheritance():
    def _test(result):
        assert result["name"] == "Wall-E"
        assert result["species"] == "dog"
        assert result["breed"] == "Pitbull"
        assert result["is_best_boy"] is True

    hybrid_dog = models.HybridDog(name="Wall-E", species="dog", breed="Pitbull", is_best_boy=True)
    _test(as_attribute_dict(hybrid_dog))
    msrest_dog = models.MsrestDog(name="Wall-E", species="dog", breed="Pitbull", is_best_boy=True)
    _test(as_attribute_dict(msrest_dog))


def test_as_attribute_dict_multipart_file():
    file_data = BytesIO(b"This is test file content")
    upload = models.FileUpload(name="test.txt", content=file_data, content_type="text/plain")

    attr_dict = as_attribute_dict(upload)
    assert attr_dict["name"] == "test.txt"
    assert attr_dict["content"] is file_data  # Should be preserved as-is for multipart files
    assert attr_dict["content_type"] == "text/plain"


def test_as_attribute_dict_with_null_object():
    def _test_non_nested(result):
        assert result["required_prop"] == "always here"
        assert "optional_prop" not in result
        assert "optional_model" not in result

    def _test_nested(result):
        assert result["required_prop"] == "outer"
        assert "optional_prop" not in result
        assert result["optional_model"]["required_prop"] == "nested"
        assert result["optional_model"]["optional_prop"] == "present"
        assert "optional_model" not in result["optional_model"]

    hybrid_model = models.HybridOptionalProps(required_prop="always here", optional_prop=None, optional_model=None)

    _test_non_nested(as_attribute_dict(hybrid_model))

    msrest_model = models.MsrestOptionalProps(required_prop="always here", optional_prop=None, optional_model=None)
    _test_non_nested(as_attribute_dict(msrest_model))

    # Test with a nested model that has a null property
    hybrid_nested = models.HybridOptionalProps(required_prop="nested", optional_prop="present", optional_model=None)
    hybrid_model = models.HybridOptionalProps(required_prop="outer", optional_prop=None, optional_model=hybrid_nested)

    _test_nested(as_attribute_dict(hybrid_model))

    msrest_nested = models.MsrestOptionalProps(required_prop="nested", optional_prop="present", optional_model=None)
    msrest_model = models.MsrestOptionalProps(required_prop="outer", optional_prop=None, optional_model=msrest_nested)
    _test_nested(as_attribute_dict(msrest_model))


def test_as_attribute_dict_nested_discriminators():
    salmon = models.Salmon(
        {
            "age": 1,
            "kind": "salmon",
            "lifePartner": {"age": 2, "kind": "shark", "sharkType": "saw"},
            "friends": [
                {
                    "age": 2,
                    "kind": "salmon",
                    "lifePartner": {"age": 3, "kind": "salmon"},
                    "hate": {
                        "key1": {"age": 4, "kind": "salmon"},
                        "key2": {"age": 2, "kind": "shark", "sharkType": "goblin"},
                    },
                },
                {"age": 3, "kind": "shark", "sharkType": "goblin"},
            ],
            "hate": {
                "key3": {"age": 3, "kind": "shark", "sharkType": "saw"},
                "key4": {
                    "age": 2,
                    "kind": "salmon",
                    "friends": [
                        {"age": 1, "kind": "salmon"},
                        {"age": 4, "kind": "shark", "sharkType": "goblin"},
                    ],
                },
            },
        }
    )
    attr_dict = as_attribute_dict(salmon)
    assert attr_dict["age"] == 1
    assert attr_dict["kind"] == "salmon"
    assert attr_dict["life_partner"]["age"] == 2
    assert attr_dict["life_partner"]["kind"] == "shark"
    assert attr_dict["life_partner"]["shark_type"] == "saw"
    assert len(attr_dict["friends"]) == 2
    assert attr_dict["friends"][0]["age"] == 2
    assert attr_dict["friends"][0]["kind"] == "salmon"
    assert attr_dict["friends"][0]["life_partner"]["age"] == 3
    assert attr_dict["friends"][0]["life_partner"]["kind"] == "salmon"
    assert len(attr_dict["friends"][0]["hate"]) == 2
    assert attr_dict["friends"][0]["hate"]["key1"]["age"] == 4
    assert attr_dict["friends"][0]["hate"]["key1"]["kind"] == "salmon"
    assert attr_dict["friends"][0]["hate"]["key2"]["age"] == 2
    assert attr_dict["friends"][0]["hate"]["key2"]["kind"] == "shark"
    assert attr_dict["friends"][0]["hate"]["key2"]["shark_type"] == "goblin"


def test_as_attribute_dict_complex_scenario():
    def _test(result):
        # Verify top-level properties
        assert result["employee_id"] == "E12345"
        assert result["first_name"] == "Jane"
        assert result["last_name"] == "Doe"
        assert result["hire_date"] == "2020-03-15"

        # Verify nested contact info
        assert result["contact"]["email"] == "jane.doe@example.com"
        assert result["contact"]["phone"] == "555-123-4567"

        # Verify list of address objects
        assert len(result["contact"]["addresses"]) == 2
        assert result["contact"]["addresses"][0]["street"] == "123 Home St"
        assert result["contact"]["addresses"][0]["city"] == "Hometown"
        assert result["contact"]["addresses"][0]["zip_code"] == "12345"

        # Verify department
        assert result["department"]["name"] == "Engineering"
        assert result["department"]["cost_center"] == "CC-ENG-123"

        # Verify collections
        assert result["skills"] == ["Python", "TypeScript", "Azure"]
        assert result["performance_ratings"] == {"2020": 4.5, "2021": 4.7, "2022": 4.8}

    # Create a complex employee object
    hybrid_employee = models.HybridEmployee(
        employee_id="E12345",
        first_name="Jane",
        last_name="Doe",
        hire_date=date(2020, 3, 15),
        contact=models.HybridContactInfo(
            email="jane.doe@example.com",
            phone="555-123-4567",
            addresses=[
                models.HybridAddress(street="123 Home St", city="Hometown", zip_code="12345"),
                models.HybridAddress(street="456 Work Ave", city="Workville", zip_code="67890"),
            ],
        ),
        department=models.HybridDepartment(name="Engineering", cost_center="CC-ENG-123"),
        skills=["Python", "TypeScript", "Azure"],
        performance_ratings={"2020": 4.5, "2021": 4.7, "2022": 4.8},
    )

    # Get full attribute dictionary
    _test(as_attribute_dict(hybrid_employee))

    # Now check with exclude_readonly=True
    attr_dict = as_attribute_dict(hybrid_employee, exclude_readonly=True)
    assert "employee_id" not in attr_dict
    assert attr_dict["first_name"] == "Jane"

    msrest_employee = models.MsrestEmployee(
        employee_id="E12345",
        first_name="Jane",
        last_name="Doe",
        hire_date=date(2020, 3, 15),
        contact=models.MsrestContactInfo(
            email="jane.doe@example.com",
            phone="555-123-4567",
            addresses=[
                models.MsrestAddress(street="123 Home St", city="Hometown", zip_code="12345"),
                models.MsrestAddress(street="456 Work Ave", city="Workville", zip_code="67890"),
            ],
        ),
        department=models.MsrestDepartment(name="Engineering", cost_center="CC-ENG-123"),
        skills=["Python", "TypeScript", "Azure"],
        performance_ratings={"2020": 4.5, "2021": 4.7, "2022": 4.8},
    )

    _test(as_attribute_dict(msrest_employee))
    # Now check with exclude_readonly=True
    attr_dict = as_attribute_dict(msrest_employee, exclude_readonly=True)
    assert "employee_id" not in attr_dict
    assert attr_dict["first_name"] == "Jane"


def test_as_attribute_dict_flatten():
    def _test(result):
        assert result["name"] == "wall-e"
        assert result["description"] == "a dog"
        assert result["age"] == 2
        assert "properties" not in result
        assert "modelDescription" not in result
        assert "model_description" not in result

    hybrid_model = models.FlattenModel(name="wall-e", description="a dog", age=2)
    msrest_model = models.MsrestFlattenModel(name="wall-e", description="a dog", age=2)

    _test(as_attribute_dict(hybrid_model))
    _test(as_attribute_dict(msrest_model))


def test_as_attribute_dict_additional_properties():
    def _tests(model):
        attr_dict = as_attribute_dict(model)
        assert attr_dict["name"] == "Buddy"
        assert "additional_properties" not in attr_dict
        assert attr_dict["birthdate"] == "2017-12-13T02:29:51Z"
        assert attr_dict["complexProperty"] == {"color": "Red"}
        assert getattr(model, "birthdate", None) is None
        assert getattr(model, "complexProperty", None) is None

    hybrid_model = models.HybridPetAPTrue(
        {"birthdate": "2017-12-13T02:29:51Z", "complexProperty": {"color": "Red"}, "name": "Buddy"}
    )
    assert getattr(hybrid_model, "additional_properties", None) is None
    _tests(hybrid_model)
    msrest_model = models.MsrestPetAPTrue(
        additional_properties={"birthdate": "2017-12-13T02:29:51Z", "complexProperty": {"color": "Red"}}, name="Buddy"
    )
    _tests(msrest_model)
    assert msrest_model.additional_properties == {
        "birthdate": "2017-12-13T02:29:51Z",
        "complexProperty": {"color": "Red"},
    }


class TestTypeHandlerRegistry:
    """Test usage of the TypeHandlerRegistry with the model_base.py serialization/deserialization mechanisms."""

    class FooModel:

        foo: str
        bar: int
        baz: float

        def __init__(self, foo: str, bar: int, baz: float):
            self.foo = foo
            self.bar = bar
            self.baz = baz

    def test_serialization_fails_no_registry(self):

        model = TestTypeHandlerRegistry.FooModel(foo="foo", bar=42, baz=3.14)
        with pytest.raises(TypeError):
            json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)

    def test_deserialize_no_registry(self):

        json_dict = {"foo": "foo", "bar": 42, "baz": 3.14}
        deserialized = _deserialize(TestTypeHandlerRegistry.FooModel, json_dict)
        # If no deserializer is registered, the input should be returned as-is
        assert deserialized == json_dict
        assert type(deserialized) is dict

    def test_serialize_external_model(self):

        @TYPE_HANDLER_REGISTRY.register_serializer(TestTypeHandlerRegistry.FooModel)
        def foo_serializer(obj: TestTypeHandlerRegistry.FooModel) -> Dict[str, Any]:
            return {"foo": obj.foo, "bar": obj.bar, "baz": obj.baz}

        model = TestTypeHandlerRegistry.FooModel(foo="foo", bar=42, baz=3.14)

        serializer = TYPE_HANDLER_REGISTRY.get_serializer(model)
        assert serializer is foo_serializer

        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == {"foo": "foo", "bar": 42, "baz": 3.14}

    def test_serialize_external_model_manual_decorator(self):

        def foo_serializer(obj: TestTypeHandlerRegistry.FooModel) -> Dict[str, Any]:
            return {"foo": obj.foo, "bar": obj.bar, "baz": obj.baz}

        TYPE_HANDLER_REGISTRY.register_serializer(TestTypeHandlerRegistry.FooModel)(foo_serializer)

        model = TestTypeHandlerRegistry.FooModel(foo="foo", bar=42, baz=3.14)
        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == {"foo": "foo", "bar": 42, "baz": 3.14}

    def test_deserialize_external_model(self):

        @TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)
        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        deserializer = TYPE_HANDLER_REGISTRY.get_deserializer(TestTypeHandlerRegistry.FooModel)

        assert type(deserializer).__name__ == "partial"
        assert getattr(deserializer, "func", None) is foo_deserializer
        assert getattr(deserializer, "args", ()) == (TestTypeHandlerRegistry.FooModel,)

        json_dict = {"foo": "foo", "bar": 42, "baz": 3.14}
        deserialized = _deserialize(TestTypeHandlerRegistry.FooModel, json_dict)
        assert isinstance(deserialized, TestTypeHandlerRegistry.FooModel)
        assert deserialized.foo == "foo"
        assert deserialized.bar == 42
        assert deserialized.baz == 3.14

    def test_deserialize_external_model_manual_decorator(self):

        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)(foo_deserializer)

        json_dict = {"foo": "foo", "bar": 42, "baz": 3.14}
        deserialized = _deserialize(TestTypeHandlerRegistry.FooModel, json_dict)
        assert isinstance(deserialized, TestTypeHandlerRegistry.FooModel)
        assert deserialized.foo == "foo"
        assert deserialized.bar == 42
        assert deserialized.baz == 3.14

    def test_serialize_external_model_in_nested_model(self):

        @TYPE_HANDLER_REGISTRY.register_serializer(TestTypeHandlerRegistry.FooModel)
        def foo_serializer(obj: TestTypeHandlerRegistry.FooModel) -> Dict[str, Any]:
            return {"foo": obj.foo, "bar": obj.bar, "baz": obj.baz}

        class GeneratedModel(HybridModel):
            dog: models.HybridDog = rest_field(visibility=["read", "create", "update", "delete", "query"])
            external: TestTypeHandlerRegistry.FooModel = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        model = GeneratedModel(
            dog=models.HybridDog(name="doggy", species="dog", breed="samoyed", is_best_boy=True),
            external=TestTypeHandlerRegistry.FooModel(foo="foo", bar=42, baz=3.14),
        )

        expected_dict = {
            "dog": {
                "name": "doggy",
                "species": "dog",
                "breed": "samoyed",
                "isBestBoy": True,
            },
            "external": {
                "foo": "foo",
                "bar": 42,
                "baz": 3.14,
            },
        }

        assert model.as_dict() == expected_dict

        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

    def test_deserialize_external_model_in_nested_model(self):

        @TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)
        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        class GeneratedModel(HybridModel):
            dog: models.HybridDog = rest_field(visibility=["read", "create", "update", "delete", "query"])
            external: TestTypeHandlerRegistry.FooModel = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        json_dict = {
            "dog": {
                "name": "doggy",
                "species": "dog",
                "breed": "samoyed",
                "isBestBoy": True,
            },
            "external": {
                "foo": "foo",
                "bar": 42,
                "baz": 3.14,
            },
        }

        deserialized = _deserialize(GeneratedModel, json_dict)

        assert isinstance(deserialized, GeneratedModel)
        assert isinstance(deserialized.dog, models.HybridDog)
        assert isinstance(deserialized.external, TestTypeHandlerRegistry.FooModel)
        assert deserialized.dog.name == "doggy"
        assert deserialized.dog.species == "dog"
        assert deserialized.dog.breed == "samoyed"
        assert deserialized.dog.is_best_boy is True
        assert deserialized.external.foo == "foo"
        assert deserialized.external.bar == 42
        assert deserialized.external.baz == 3.14

    def test_serialize_deserialize_list_of_external_models(self):

        @TYPE_HANDLER_REGISTRY.register_serializer(TestTypeHandlerRegistry.FooModel)
        def foo_serializer(obj: TestTypeHandlerRegistry.FooModel) -> Dict[str, Any]:
            return {"foo": obj.foo, "bar": obj.bar, "baz": obj.baz}

        @TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)
        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        class GeneratedModel(HybridModel):
            externals: List[TestTypeHandlerRegistry.FooModel] = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        model = GeneratedModel(
            externals=[
                TestTypeHandlerRegistry.FooModel(foo="foo1", bar=1, baz=1.1),
                TestTypeHandlerRegistry.FooModel(foo="foo2", bar=2, baz=2.2),
            ]
        )

        expected_dict = {
            "externals": [
                {"foo": "foo1", "bar": 1, "baz": 1.1},
                {"foo": "foo2", "bar": 2, "baz": 2.2},
            ]
        }

        assert model.as_dict() == expected_dict

        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

        # Deserialization
        deserialized = _deserialize(GeneratedModel, expected_dict)
        assert isinstance(deserialized, GeneratedModel)
        assert isinstance(deserialized.externals, list)
        assert len(deserialized.externals) == 2
        assert all(isinstance(item, TestTypeHandlerRegistry.FooModel) for item in deserialized.externals)
        assert deserialized.externals[0].foo == "foo1"
        assert deserialized.externals[0].bar == 1
        assert deserialized.externals[0].baz == 1.1
        assert deserialized.externals[1].foo == "foo2"
        assert deserialized.externals[1].bar == 2
        assert deserialized.externals[1].baz == 2.2

    def test_serialize_deserialize_dict_of_external_models(self):

        @TYPE_HANDLER_REGISTRY.register_serializer(TestTypeHandlerRegistry.FooModel)
        def foo_serializer(obj: TestTypeHandlerRegistry.FooModel) -> Dict[str, Any]:
            return {"foo": obj.foo, "bar": obj.bar, "baz": obj.baz}

        @TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)
        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        class GeneratedModel(HybridModel):
            externals: Dict[str, TestTypeHandlerRegistry.FooModel] = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        model = GeneratedModel(
            externals={
                "first": TestTypeHandlerRegistry.FooModel(foo="foo1", bar=1, baz=1.1),
                "second": TestTypeHandlerRegistry.FooModel(foo="foo2", bar=2, baz=2.2),
            }
        )

        expected_dict = {
            "externals": {
                "first": {"foo": "foo1", "bar": 1, "baz": 1.1},
                "second": {"foo": "foo2", "bar": 2, "baz": 2.2},
            }
        }

        assert model.as_dict() == expected_dict

        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

        # Deserialization
        deserialized = _deserialize(GeneratedModel, expected_dict)
        assert isinstance(deserialized, GeneratedModel)
        assert isinstance(deserialized.externals, dict)
        assert len(deserialized.externals) == 2
        assert all(isinstance(item, TestTypeHandlerRegistry.FooModel) for item in deserialized.externals.values())
        assert deserialized.externals["first"].foo == "foo1"
        assert deserialized.externals["first"].bar == 1
        assert deserialized.externals["first"].baz == 1.1
        assert deserialized.externals["second"].foo == "foo2"
        assert deserialized.externals["second"].bar == 2
        assert deserialized.externals["second"].baz == 2.2

    def test_serialize_deserialize_optional_external_model(self):

        @TYPE_HANDLER_REGISTRY.register_serializer(TestTypeHandlerRegistry.FooModel)
        def foo_serializer(obj: TestTypeHandlerRegistry.FooModel) -> Dict[str, Any]:
            return {"foo": obj.foo, "bar": obj.bar, "baz": obj.baz}

        @TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)
        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        class GeneratedModel(HybridModel):
            external: Optional[TestTypeHandlerRegistry.FooModel] = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        # Test with the optional model present
        model = GeneratedModel(external=TestTypeHandlerRegistry.FooModel(foo="foo", bar=42, baz=3.14))

        expected_dict = {"external": {"foo": "foo", "bar": 42, "baz": 3.14}}

        assert model.as_dict() == expected_dict
        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

        # Deserialization
        deserialized = _deserialize(GeneratedModel, expected_dict)
        assert isinstance(deserialized, GeneratedModel)
        assert isinstance(deserialized.external, TestTypeHandlerRegistry.FooModel)
        assert deserialized.external.foo == "foo"
        assert deserialized.external.bar == 42
        assert deserialized.external.baz == 3.14

        # Test with the optional model as None
        model = GeneratedModel(external=None)
        expected_dict = {}
        assert model.as_dict() == expected_dict
        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

        # Deserialization
        deserialized = _deserialize(GeneratedModel, expected_dict)
        assert isinstance(deserialized, GeneratedModel)
        assert deserialized.external is None

    def test_serialize_deserialize_union_external_model(self):

        @TYPE_HANDLER_REGISTRY.register_serializer(TestTypeHandlerRegistry.FooModel)
        def foo_serializer(obj: TestTypeHandlerRegistry.FooModel) -> Dict[str, Any]:
            return {"foo": obj.foo, "bar": obj.bar, "baz": obj.baz}

        @TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)
        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        class GeneratedModel(HybridModel):
            external: Union[str, TestTypeHandlerRegistry.FooModel] = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        # Test with the union as the external model
        model = GeneratedModel(external=TestTypeHandlerRegistry.FooModel(foo="foo", bar=42, baz=3.14))

        expected_dict = {"external": {"foo": "foo", "bar": 42, "baz": 3.14}}

        assert model.as_dict() == expected_dict
        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

        # Deserialization
        deserialized = _deserialize(GeneratedModel, expected_dict)
        assert isinstance(deserialized, GeneratedModel)
        assert isinstance(deserialized.external, TestTypeHandlerRegistry.FooModel)
        assert deserialized.external.foo == "foo"
        assert deserialized.external.bar == 42
        assert deserialized.external.baz == 3.14

        # Test with the union as a string
        model = GeneratedModel(external="just a string")
        expected_dict = {"external": "just a string"}
        assert model.as_dict() == expected_dict
        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

        # Deserialization
        deserialized = _deserialize(GeneratedModel, expected_dict)
        assert isinstance(deserialized, GeneratedModel)
        assert isinstance(deserialized.external, str)
        assert deserialized.external == "just a string"

    def test_deserialize_union_with_generated_model(self):
        class GeneratedModel(HybridModel):
            name: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
            value: int = rest_field(visibility=["read", "create", "update", "delete", "query"])

        class ContainerModel(HybridModel):
            item: Union[TestTypeHandlerRegistry.FooModel, GeneratedModel] = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        @TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)
        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            if "foo" not in data:
                raise ValueError("Missing 'foo' key for FooModel deserialization")
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        input_dict = {"item": {"foo": "foo", "bar": 42, "baz": 3.14}}
        deserialized = _deserialize(ContainerModel, input_dict)
        assert isinstance(deserialized, ContainerModel)
        assert isinstance(deserialized.item, TestTypeHandlerRegistry.FooModel)
        assert deserialized.item.foo == "foo"
        assert deserialized.item.bar == 42
        assert deserialized.item.baz == 3.14

        input_dict = {"item": {"name": "generated", "value": 100}}
        deserialized = _deserialize(ContainerModel, input_dict)
        assert isinstance(deserialized, ContainerModel)
        assert isinstance(deserialized.item, GeneratedModel)
        assert deserialized.item.name == "generated"
        assert deserialized.item.value == 100

    def test_multiple_external_type_deserialization_scenario(self):
        # Here we test a scenario where we have a generated model containing a union of multiple external types.
        # We register a deserializer predicate that will match all of the external types, and the handler function
        # will inspect the input data to determine which type to instantiate.

        class ExternalModelA:
            def __init__(self, foo: str, bar: Optional[int] = None):
                self.foo = foo
                self.bar = bar

        class ExternalModelB:
            def __init__(self, biz: int, baz: Optional[str] = None):
                self.biz = biz
                self.baz = baz

        class ContainerModel(HybridModel):
            item: Union[ExternalModelA, ExternalModelB] = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        def ext_deserializer(cls: Type, data: Dict[str, Any]) -> Union[ExternalModelA, ExternalModelB]:
            if "foo" in data:
                return ExternalModelA(foo=data["foo"], bar=data.get("bar"))
            elif "biz" in data:
                return ExternalModelB(biz=data["biz"], baz=data.get("baz"))
            else:
                raise ValueError("Invalid data for deserialization")

        TYPE_HANDLER_REGISTRY.register_deserializer(lambda t: t in (ExternalModelA, ExternalModelB))(ext_deserializer)

        input_dict = {"item": {"foo": "foo_value", "bar": 123}}
        deserialized = _deserialize(ContainerModel, input_dict)
        assert isinstance(deserialized, ContainerModel)
        assert isinstance(deserialized.item, ExternalModelA)
        assert deserialized.item.foo == "foo_value"
        assert deserialized.item.bar == 123

        input_dict = {"item": {"biz": 456, "baz": "baz_value"}}
        deserialized = _deserialize(ContainerModel, input_dict)
        assert isinstance(deserialized, ContainerModel)
        assert isinstance(deserialized.item, ExternalModelB)
        assert deserialized.item.biz == 456
        assert deserialized.item.baz == "baz_value"

    def test_multiple_external_type_deserialization_polymorphic_scenario(self):
        # Similar to the previous test, but here we have one external type inheriting from another.
        # The deserializer function will need to handle this inheritance relationship and instantiation priority.
        class ExternalModelA:
            def __init__(self, foo: str, bar: Optional[int] = None):
                self.foo = foo
                self.bar = bar

        class ExternalModelB(ExternalModelA):
            def __init__(self, foo: str, bar: Optional[int] = None, baz: Optional[float] = None):
                super().__init__(foo, bar)
                self.baz = baz

        class ContainerModel(HybridModel):
            item: Union[ExternalModelA, ExternalModelB] = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        def ext_deserializer(cls: Type, data: Dict[str, Any]) -> Union[ExternalModelA, ExternalModelB]:
            if "baz" in data:
                return ExternalModelB(foo=data["foo"], bar=data.get("bar"), baz=data.get("baz"))
            elif "foo" in data:
                return ExternalModelA(foo=data["foo"], bar=data.get("bar"))
            else:
                raise ValueError("Invalid data for deserialization")

        TYPE_HANDLER_REGISTRY.register_deserializer(lambda t: t in (ExternalModelA, ExternalModelB))(ext_deserializer)

        input_dict = {"item": {"foo": "foo_value", "bar": 123}}
        deserialized = _deserialize(ContainerModel, input_dict)
        assert isinstance(deserialized, ContainerModel)
        assert isinstance(deserialized.item, ExternalModelA)
        assert not isinstance(deserialized.item, ExternalModelB)
        assert deserialized.item.foo == "foo_value"
        assert deserialized.item.bar == 123

        input_dict = {"item": {"foo": "foo_value", "bar": 123, "baz": 3.14}}
        deserialized = _deserialize(ContainerModel, input_dict)
        assert isinstance(deserialized, ContainerModel)
        assert isinstance(deserialized.item, ExternalModelB)
        assert deserialized.item.foo == "foo_value"
        assert deserialized.item.bar == 123
        assert deserialized.item.baz == 3.14

    def test_serialize_deserialize_deep_nested_external_model_in_generated_model(self):

        @TYPE_HANDLER_REGISTRY.register_serializer(TestTypeHandlerRegistry.FooModel)
        def foo_serializer(obj: TestTypeHandlerRegistry.FooModel) -> Dict[str, Any]:
            return {"foo": obj.foo, "bar": obj.bar, "baz": obj.baz}

        @TYPE_HANDLER_REGISTRY.register_deserializer(TestTypeHandlerRegistry.FooModel)
        def foo_deserializer(cls, data: Dict[str, Any]) -> TestTypeHandlerRegistry.FooModel:
            return TestTypeHandlerRegistry.FooModel(foo=data["foo"], bar=data["bar"], baz=data["baz"])

        class NestedModel(HybridModel):
            foo: TestTypeHandlerRegistry.FooModel = rest_field(
                visibility=["read", "create", "update", "delete", "query"]
            )

        class ChildModel(HybridModel):
            nested: NestedModel = rest_field(visibility=["read", "create", "update", "delete", "query"])

        class BaseModel(HybridModel):
            child: ChildModel = rest_field(visibility=["read", "create", "update", "delete", "query"])

        model = BaseModel(
            child=ChildModel(nested=NestedModel(foo=TestTypeHandlerRegistry.FooModel(foo="foo", bar=42, baz=3.14)))
        )

        expected_dict = {"child": {"nested": {"foo": {"foo": "foo", "bar": 42, "baz": 3.14}}}}

        assert model.as_dict() == expected_dict
        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

        # Deserialization
        deserialized = _deserialize(BaseModel, expected_dict)
        assert isinstance(deserialized, BaseModel)
        assert isinstance(deserialized.child, ChildModel)
        assert isinstance(deserialized.child.nested, NestedModel)
        assert deserialized.child.nested.foo.foo == "foo"
        assert deserialized.child.nested.foo.bar == 42
        assert deserialized.child.nested.foo.baz == 3.14

    def test_serialize_deserialize_external_model_with_predicates(self):

        import dataclasses

        @dataclasses.dataclass
        class SampleModel:
            foo: str
            bar: int

        @dataclasses.dataclass
        class SampleModel2:
            biz: str
            baz: int

        class GeneratedModel(HybridModel):
            foo: SampleModel = rest_field(visibility=["read", "create", "update", "delete", "query"])
            bar: SampleModel2 = rest_field(visibility=["read", "create", "update", "delete", "query"])

        @TYPE_HANDLER_REGISTRY.register_serializer(lambda obj: dataclasses.is_dataclass(obj))
        def foo_serializer(obj) -> Dict[str, Any]:
            return dataclasses.asdict(obj)

        @TYPE_HANDLER_REGISTRY.register_deserializer(lambda t: dataclasses.is_dataclass(t))
        def foo_deserializer(cls: Type, data: Dict[str, Any]) -> Any:
            return cls(**data)

        model = SampleModel(foo="foo", bar=42)
        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == {"foo": "foo", "bar": 42}

        model = GeneratedModel(
            foo=SampleModel(foo="foo", bar=42),
            bar=SampleModel2(biz="biz", baz=3),
        )

        expected_dict = {
            "foo": {"foo": "foo", "bar": 42},
            "bar": {"biz": "biz", "baz": 3},
        }
        assert model.as_dict() == expected_dict
        json_str = json.dumps(model, cls=SdkJSONEncoder, exclude_readonly=True)
        assert json.loads(json_str) == expected_dict

        # Deserialization
        deserialized = _deserialize(GeneratedModel, expected_dict)
        assert isinstance(deserialized, GeneratedModel)
        assert isinstance(deserialized.foo, SampleModel)
        assert isinstance(deserialized.bar, SampleModel2)
        assert deserialized.foo.foo == "foo"
        assert deserialized.foo.bar == 42
        assert deserialized.bar.biz == "biz"
        assert deserialized.bar.baz == 3

    def test_serialize_types_caching(self):

        class ModelA:
            pass

        class ModelB:
            pass

        def serializer_a(obj: ModelA) -> Dict[str, Any]:
            return {"type": "A"}

        def serialize_a2(obj: ModelA) -> Dict[str, Any]:
            return {"type": "A2"}

        def serializer_b(obj: ModelB) -> Dict[str, Any]:
            return {"type": "B"}

        TYPE_HANDLER_REGISTRY.register_serializer(ModelA)(serializer_a)
        TYPE_HANDLER_REGISTRY.register_serializer(ModelB)(serializer_b)

        model_a = ModelA()
        model_b = ModelB()

        # First retrieval should populate the cache
        serializer = TYPE_HANDLER_REGISTRY.get_serializer(model_a)
        assert serializer is serializer_a
        assert TYPE_HANDLER_REGISTRY._serializer_cache[ModelA] is serializer_a

        # Second retrieval should hit the cache
        serializer = TYPE_HANDLER_REGISTRY.get_serializer(model_a)
        assert serializer is serializer_a

        # Retrieval for a different type
        serializer = TYPE_HANDLER_REGISTRY.get_serializer(model_b)
        assert serializer is serializer_b
        assert TYPE_HANDLER_REGISTRY._serializer_cache[ModelB] is serializer_b

        # Again, should hit the cache
        serializer = TYPE_HANDLER_REGISTRY.get_serializer(model_b)
        assert serializer is serializer_b

        # Now, re-register a different serializer for ModelA
        TYPE_HANDLER_REGISTRY.register_serializer(ModelA)(serialize_a2)
        serializer = TYPE_HANDLER_REGISTRY.get_serializer(model_a)
        assert serializer is serialize_a2
        assert TYPE_HANDLER_REGISTRY._serializer_cache[ModelA] is serialize_a2

    def test_deserialize_types_caching(self):

        class ModelA:
            def __init__(self):
                self.type = None

        class ModelB:
            def __init__(self):
                self.type = None

        def deserializer_a(cls, data: Dict[str, Any]) -> ModelA:
            obj = ModelA()
            obj.type = data["type"]
            return obj

        def deserialize_a2(cls, data: Dict[str, Any]) -> ModelA:
            obj = ModelA()
            obj.type = data["type"] + "2"
            return obj

        def deserializer_b(cls, data: Dict[str, Any]) -> ModelB:
            obj = ModelB()
            obj.type = data["type"]
            return obj

        TYPE_HANDLER_REGISTRY.register_deserializer(ModelA)(deserializer_a)
        TYPE_HANDLER_REGISTRY.register_deserializer(ModelB)(deserializer_b)

        json_dict_a = {"type": "A"}
        json_dict_b = {"type": "B"}

        # First retrieval should populate the cache
        deserializer = TYPE_HANDLER_REGISTRY.get_deserializer(ModelA)
        assert getattr(deserializer, "func", None) is deserializer_a
        assert TYPE_HANDLER_REGISTRY._deserializer_cache[ModelA] is deserializer

        # Second retrieval should hit the cache
        deserializer = TYPE_HANDLER_REGISTRY.get_deserializer(ModelA)
        assert getattr(deserializer, "func", None) is deserializer_a

        # Retrieval for a different type
        deserializer = TYPE_HANDLER_REGISTRY.get_deserializer(ModelB)
        assert getattr(deserializer, "func", None) is deserializer_b
        assert TYPE_HANDLER_REGISTRY._deserializer_cache[ModelB] is deserializer

        # Again, should hit the cache
        deserializer = TYPE_HANDLER_REGISTRY.get_deserializer(ModelB)
        assert getattr(deserializer, "func", None) is deserializer_b

        # Now, re-register a different deserializer for ModelA
        TYPE_HANDLER_REGISTRY.register_deserializer(ModelA)(deserialize_a2)
        deserializer = TYPE_HANDLER_REGISTRY.get_deserializer(ModelA)
        assert getattr(deserializer, "func", None) is deserialize_a2
        assert TYPE_HANDLER_REGISTRY._deserializer_cache[ModelA] is deserializer

        # Test that deserialization works as expected
        deserialized_a = _deserialize(ModelA, json_dict_a)
        assert isinstance(deserialized_a, ModelA)
        assert deserialized_a.type == "A2"


class TestBackcompatPropertyMatrix:
    """
    Systematic test matrix for DPG model property backcompat scenarios.

    Tests all combinations of 5 key dimensions:
    1. wireName: same/different from attr_name
    2. attr_name: normal/padded (reserved word)
    3. original_tsp_name: None/present (TSP name before padding)
    4. visibility: readonly/readwrite (affects exclude_readonly)
    5. structure: regular/nested/flattened models

    COMPLETE TEST MATRIX:
    ┌───────┬─────────────┬──────────────┬─────────────────┬────────────┬──────────────┬─────────────────────────────┐
    │ Test  │ Wire Name   │ Attr Name    │ Original TSP    │ Visibility │ Structure    │ Expected Behavior           │
    ├───────┼─────────────┼──────────────┼─────────────────┼────────────┼──────────────┼─────────────────────────────┤
    │ 1a    │ same        │ normal       │ None            │ readwrite  │ regular      │ attr_name                   │
    │ 1b    │ same        │ normal       │ None            │ readonly   │ regular      │ attr_name (exclude test)    │
    │ 2a    │ different   │ normal       │ None            │ readwrite  │ regular      │ attr_name                   │
    │ 2b    │ different   │ normal       │ None            │ readonly   │ regular      │ attr_name (exclude test)    │
    │ 3a    │ same        │ padded       │ present         │ readwrite  │ regular      │ original_tsp_name           │
    │ 3b    │ same        │ padded       │ present         │ readonly   │ regular      │ original_tsp_name (exclude) │
    │ 4a    │ different   │ padded       │ present         │ readwrite  │ regular      │ original_tsp_name           │
    │ 4b    │ different   │ padded       │ present         │ readonly   │ regular      │ original_tsp_name (exclude) │
    │ 5a    │ various     │ mixed        │ mixed           │ mixed      │ nested       │ recursive backcompat        │
    │ 6a    │ same        │ padded       │ present         │ readwrite  │ flat-contain │ flattened + backcompat      │
    │ 6b    │ various     │ mixed        │ mixed           │ mixed      │ flat-props   │ flattened props backcompat  │
    │ 6c    │ various     │ mixed        │ mixed           │ readonly   │ flat-mixed   │ flattened + exclude         │
    └───────┴─────────────┴──────────────┴─────────────────┴────────────┴──────────────┴─────────────────────────────┘
    """

    # ========== DIMENSION 1-4 COMBINATIONS: REGULAR STRUCTURE ==========

    def test_1a_same_wire_normal_attr_no_original_readwrite_regular(self):
        """Wire=attr, normal attr, no original, readwrite, regular model"""

        class RegularModel(HybridModel):
            field_name: str = rest_field()

        model = RegularModel(field_name="value")

        # Should use attr_name (same as wire name)
        assert attribute_list(model) == ["field_name"]
        assert as_attribute_dict(model) == {"field_name": "value"}
        assert as_attribute_dict(model, exclude_readonly=True) == {"field_name": "value"}
        assert getattr(model, "field_name") == "value"
        assert get_backcompat_attr_name(model, "field_name") == "field_name"

    def test_1b_same_wire_normal_attr_no_original_readonly_regular(self):
        """Wire=attr, normal attr, no original, readonly, regular model"""

        class ReadonlyModel(HybridModel):
            field_name: str = rest_field(visibility=["read"])

        model = ReadonlyModel(field_name="value")

        # Should use attr_name, but excluded when exclude_readonly=True
        assert attribute_list(model) == ["field_name"]
        assert as_attribute_dict(model) == {"field_name": "value"}
        assert as_attribute_dict(model, exclude_readonly=True) == {}
        assert getattr(model, "field_name") == "value"
        assert get_backcompat_attr_name(model, "field_name") == "field_name"

    def test_2a_different_wire_normal_attr_no_original_readwrite_regular(self):
        """Wire≠attr, normal attr, no original, readwrite, regular model"""

        class DifferentWireModel(HybridModel):
            client_field: str = rest_field(name="wireField")

        model = DifferentWireModel(client_field="value")

        # Should use attr_name (wire name is different)
        assert attribute_list(model) == ["client_field"]
        assert as_attribute_dict(model) == {"client_field": "value"}
        # Verify wire representation uses different name
        assert dict(model) == {"wireField": "value"}
        assert getattr(model, "client_field") == "value"
        assert get_backcompat_attr_name(model, "client_field") == "client_field"

    def test_2b_different_wire_normal_attr_no_original_readonly_regular(self):
        """Wire≠attr, normal attr, no original, readonly, regular model"""

        class ReadonlyDifferentWireModel(HybridModel):
            client_field: str = rest_field(name="wireField", visibility=["read"])

        model = ReadonlyDifferentWireModel(client_field="value")

        # Should use attr_name, excluded when exclude_readonly=True
        assert attribute_list(model) == ["client_field"]
        assert as_attribute_dict(model) == {"client_field": "value"}
        assert as_attribute_dict(model, exclude_readonly=True) == {}
        assert getattr(model, "client_field") == "value"
        assert get_backcompat_attr_name(model, "client_field") == "client_field"

    def test_3a_same_wire_padded_attr_with_original_readwrite_regular(self):
        """Wire=original, padded attr, original present, readwrite, regular model"""

        class PaddedModel(HybridModel):
            keys_property: str = rest_field(original_tsp_name="keys")

        model = PaddedModel(keys_property="value")

        # Should use original_tsp_name when available
        assert attribute_list(model) == ["keys_property"]
        assert as_attribute_dict(model) == {"keys_property": "value"}
        assert get_backcompat_attr_name(model, "keys_property") == "keys"
        assert getattr(model, "keys_property") == "value"
        assert set(model.keys()) == {"keys_property"}

    def test_3b_same_wire_padded_attr_with_original_readonly_regular(self):
        """Wire=original, padded attr, original present, readonly, regular model"""

        class ReadonlyPaddedModel(HybridModel):
            keys_property: str = rest_field(visibility=["read"], original_tsp_name="keys")

        model = ReadonlyPaddedModel(keys_property="value")

        assert attribute_list(model) == ["keys_property"]
        assert as_attribute_dict(model) == {"keys_property": "value"}
        assert as_attribute_dict(model, exclude_readonly=True) == {}
        assert get_backcompat_attr_name(model, "keys_property") == "keys"
        assert getattr(model, "keys_property") == "value"
        assert set(model.keys()) == {"keys_property"}

    def test_4a_different_wire_padded_attr_with_original_readwrite_regular(self):
        """Wire≠original, padded attr, original present, readwrite, regular model"""

        class DifferentWirePaddedModel(HybridModel):
            clear_property: str = rest_field(name="clearWire", original_tsp_name="clear")

        model = DifferentWirePaddedModel(clear_property="value")

        assert attribute_list(model) == ["clear_property"]
        assert as_attribute_dict(model) == {"clear_property": "value"}
        # Verify wire uses different name
        assert dict(model) == {"clearWire": "value"}
        assert getattr(model, "clear_property") == "value"
        assert set(model.keys()) == {"clearWire"}

    def test_4b_different_wire_padded_attr_with_original_readonly_regular(self):
        """Wire≠original, padded attr, original present, readonly, regular model"""

        class ReadonlyDifferentWirePaddedModel(HybridModel):
            pop_property: str = rest_field(name="popWire", visibility=["read"], original_tsp_name="pop")

        model = ReadonlyDifferentWirePaddedModel(pop_property="value")

        assert attribute_list(model) == ["pop_property"]
        assert as_attribute_dict(model) == {"pop_property": "value"}
        assert as_attribute_dict(model, exclude_readonly=True) == {}
        assert getattr(model, "pop_property") == "value"
        assert set(model.keys()) == {"popWire"}

    # ========== DIMENSION 5: STRUCTURE VARIATIONS ==========

    def test_5a_nested_model_backcompat_recursive(self):
        """Nested models with mixed backcompat scenarios"""

        class NestedBackcompatModel(HybridModel):
            keys_property: str = rest_field(name="keysWire", original_tsp_name="keys")
            normal_field: str = rest_field(name="normalWire")

        class ParentModel(HybridModel):
            nested: NestedBackcompatModel = rest_field()
            items_property: str = rest_field(name="itemsWire", original_tsp_name="items")

        nested_model = NestedBackcompatModel(keys_property="nested_keys", normal_field="nested_normal")
        parent_model = ParentModel(nested=nested_model, items_property="parent_items")

        # Test nested model independently
        nested_attrs = attribute_list(nested_model)
        assert set(nested_attrs) == {"keys_property", "normal_field"}

        nested_dict = as_attribute_dict(nested_model)
        assert nested_dict == {"keys_property": "nested_keys", "normal_field": "nested_normal"}

        # Test parent model with recursive backcompat
        parent_attrs = attribute_list(parent_model)
        assert set(parent_attrs) == {"nested", "items_property"}

        parent_dict = as_attribute_dict(parent_model)
        expected_parent = {
            "nested": {"keys_property": "nested_keys", "normal_field": "nested_normal"},
            "items_property": "parent_items",
        }
        assert parent_dict == expected_parent

        assert getattr(nested_model, "keys_property") == "nested_keys"
        assert getattr(parent_model, "items_property") == "parent_items"

        assert set(nested_model.keys()) == {"keysWire", "normalWire"}
        assert set(nested_model.items()) == {("keysWire", "nested_keys"), ("normalWire", "nested_normal")}
        assert set(parent_model.keys()) == {"nested", "itemsWire"}
        assert len(parent_model.items()) == 2
        assert ("nested", parent_model.nested) in parent_model.items()
        assert ("itemsWire", "parent_items") in parent_model.items()

    def test_6a_flattened_container_with_backcompat(self):
        """Flattened property where container has backcompat (keys_property → keys)"""

        # Helper model for flattening content
        class ContentModel(HybridModel):
            name: str = rest_field()
            description: str = rest_field()

        class FlattenedContainerModel(HybridModel):
            id: str = rest_field()
            update_property: ContentModel = rest_field(original_tsp_name="update")

            __flattened_items = ["name", "description"]

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                _flattened_input = {k: kwargs.pop(k) for k in kwargs.keys() & self.__flattened_items}
                super().__init__(*args, **kwargs)
                for k, v in _flattened_input.items():
                    setattr(self, k, v)

            def __getattr__(self, name: str) -> Any:
                if name in self.__flattened_items:
                    if self.update_property is None:
                        return None
                    return getattr(self.update_property, name)
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

            def __setattr__(self, key: str, value: Any) -> None:
                if key in self.__flattened_items:
                    if self.update_property is None:
                        self.update_property = self._attr_to_rest_field["update_property"]._class_type()
                    setattr(self.update_property, key, value)
                else:
                    super().__setattr__(key, value)

        model = FlattenedContainerModel(id="test_id", name="flattened_name", description="flattened_desc")

        # Flattened items should appear at top level
        attrs = attribute_list(model)
        assert set(attrs) == {"id", "name", "description"}
        assert getattr(model, "name") == "flattened_name"
        assert getattr(model, "description") == "flattened_desc"

        # Flattened dict should use top-level names
        attr_dict = as_attribute_dict(model)
        expected = {"id": "test_id", "name": "flattened_name", "description": "flattened_desc"}
        assert attr_dict == expected

        assert get_backcompat_attr_name(model, "update_property") == "update"

        assert set(model.keys()) == {"id", "update_property"}

    def test_6b_flattened_properties_with_backcompat(self):
        """Flattened properties themselves have backcompat (type_property → type)"""

        class BackcompatContentModel(HybridModel):
            values_property: str = rest_field(name="valuesWire", original_tsp_name="values")
            get_property: str = rest_field(name="getWire", original_tsp_name="get")

        class FlattenedPropsBackcompatModel(HybridModel):
            name: str = rest_field()
            properties: BackcompatContentModel = rest_field()

            __flattened_items = ["values_property", "get_property"]

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                _flattened_input = {k: kwargs.pop(k) for k in kwargs.keys() & self.__flattened_items}
                super().__init__(*args, **kwargs)
                for k, v in _flattened_input.items():
                    setattr(self, k, v)

            def __getattr__(self, name: str) -> Any:
                if name in self.__flattened_items:
                    if self.properties is None:
                        return None
                    return getattr(self.properties, name)
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

            def __setattr__(self, key: str, value: Any) -> None:
                if key in self.__flattened_items:
                    if self.properties is None:
                        self.properties = self._attr_to_rest_field["properties"]._class_type()
                    setattr(self.properties, key, value)
                else:
                    super().__setattr__(key, value)

        model = FlattenedPropsBackcompatModel(
            name="test_name", values_property="test_values", get_property="test_class"
        )

        # Should use original names for flattened properties
        attrs = attribute_list(model)
        assert set(attrs) == {"name", "values_property", "get_property"}
        assert get_backcompat_attr_name(model, "values_property") == "values"
        assert "test_name" in model.values()

        attr_dict = as_attribute_dict(model)
        expected = {"name": "test_name", "values_property": "test_values", "get_property": "test_class"}
        assert attr_dict == expected

    def test_6c_flattened_with_readonly_exclusion(self):
        """Flattened model with readonly properties and exclude_readonly behavior"""

        class ReadonlyContentModel(HybridModel):
            setdefault_property: str = rest_field(name="readonlyWire", original_tsp_name="setdefault")
            popitem_property: str = rest_field(name="readwriteWire", original_tsp_name="popitem")

        class FlattenedReadonlyModel(HybridModel):
            get_property: str = rest_field(name="getProperty", original_tsp_name="get", visibility=["read"])
            properties: ReadonlyContentModel = rest_field()

            __flattened_items = ["setdefault_property", "popitem_property"]

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                _flattened_input = {k: kwargs.pop(k) for k in kwargs.keys() & self.__flattened_items}
                super().__init__(*args, **kwargs)
                for k, v in _flattened_input.items():
                    setattr(self, k, v)

            def __getattr__(self, name: str) -> Any:
                if name in self.__flattened_items:
                    if self.properties is None:
                        return None
                    return getattr(self.properties, name)
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

            def __setattr__(self, key: str, value: Any) -> None:
                if key in self.__flattened_items:
                    if self.properties is None:
                        self.properties = self._attr_to_rest_field["properties"]._class_type()
                    setattr(self.properties, key, value)
                else:
                    super().__setattr__(key, value)

        model = FlattenedReadonlyModel(
            get_property="test_get", setdefault_property="setdefault", popitem_property="readwrite_value"
        )

        # All properties included by default
        full_dict = as_attribute_dict(model, exclude_readonly=False)
        expected_full = {
            "get_property": "test_get",
            "setdefault_property": "setdefault",
            "popitem_property": "readwrite_value",
        }
        assert full_dict == expected_full

        # Readonly properties excluded when requested
        filtered_dict = as_attribute_dict(model, exclude_readonly=True)
        expected_filtered = {"setdefault_property": "setdefault", "popitem_property": "readwrite_value"}
        assert filtered_dict == expected_filtered

        attribute_list_result = attribute_list(model)
        expected_attrs = {"get_property", "setdefault_property", "popitem_property"}
        assert set(attribute_list_result) == expected_attrs
        assert get_backcompat_attr_name(model, "setdefault_property") == "setdefault"
        assert get_backcompat_attr_name(model, "popitem_property") == "popitem"
        assert getattr(model, "get_property") == "test_get"

    # ========== EDGE CASES ==========

    def test_mixed_combinations_comprehensive(self):
        """Comprehensive test mixing all backcompat scenarios in one model"""

        class ComprehensiveModel(HybridModel):
            # Case 1: Normal field, same wire name, no original
            normal_field: str = rest_field()

            # Case 2: Normal field, different wire name, no original
            different_wire: str = rest_field(name="wireNameDifferent")

            # Case 3: Padded field with original, same wire name
            keys_property: str = rest_field(original_tsp_name="keys")

            # Case 4: Padded field with original, different wire name
            values_property: str = rest_field(name="valuesWire", original_tsp_name="values")

            # Case 5: Readonly field with original
            items_property: str = rest_field(name="itemsWire", visibility=["read"], original_tsp_name="items")

        model = ComprehensiveModel(
            normal_field="normal",
            different_wire="different",
            keys_property="keys_val",
            values_property="values_val",
            items_property="items_val",
        )

        # attribute_list should use backcompat names where available
        attrs = attribute_list(model)
        expected_attrs = {"normal_field", "different_wire", "keys_property", "values_property", "items_property"}
        assert set(attrs) == expected_attrs
        assert get_backcompat_attr_name(model, "keys_property") == "keys"
        assert get_backcompat_attr_name(model, "values_property") == "values"
        assert get_backcompat_attr_name(model, "items_property") == "items"
        assert get_backcompat_attr_name(model, "normal_field") == "normal_field"
        assert get_backcompat_attr_name(model, "different_wire") == "different_wire"
        assert getattr(model, "keys_property") == "keys_val"
        assert getattr(model, "values_property") == "values_val"
        assert getattr(model, "items_property") == "items_val"
        assert getattr(model, "normal_field") == "normal"
        assert getattr(model, "different_wire") == "different"

        # Full as_attribute_dict
        full_dict = as_attribute_dict(model)
        expected_full = {
            "normal_field": "normal",
            "different_wire": "different",
            "keys_property": "keys_val",
            "values_property": "values_val",
            "items_property": "items_val",
        }
        assert full_dict == expected_full

        # Exclude readonly
        filtered_dict = as_attribute_dict(model, exclude_readonly=True)
        expected_filtered = {
            "normal_field": "normal",
            "different_wire": "different",
            "keys_property": "keys_val",
            "values_property": "values_val",
            # "items_property" excluded because it's readonly
        }
        assert filtered_dict == expected_filtered

        # Verify wire representations use correct wire names
        wire_dict = dict(model)
        expected_wire = {
            "normal_field": "normal",  # same as attr
            "wireNameDifferent": "different",  # different wire name
            "keys_property": "keys_val",  # same as attr (padded)
            "valuesWire": "values_val",  # different wire name
            "itemsWire": "items_val",  # different wire name
        }
        assert wire_dict == expected_wire

    def test_no_backcompat_fallback(self):
        """Test fallback behavior when no backcompat mapping exists"""

        class NoBackcompatModel(HybridModel):
            padded_attr: str = rest_field(name="wireField")
            # Note: No original_tsp_name set, so no backcompat should occur

        model = NoBackcompatModel(padded_attr="value")

        # Should fall back to using actual attribute names
        assert attribute_list(model) == ["padded_attr"]
        assert as_attribute_dict(model) == {"padded_attr": "value"}
        assert dict(model) == {"wireField": "value"}

    def test_property_with_padding_in_actual_name(self):
        """Test handling of properties that have padding in their actual attribute names"""

        class PaddingInNameModel(HybridModel):
            keys_property: str = rest_field(name="myKeys")

        model = PaddingInNameModel(keys_property="value")
        # Should use actual attribute name since no original_tsp_name is set
        assert attribute_list(model) == ["keys_property"]
        assert as_attribute_dict(model) == {"keys_property": "value"}
        assert dict(model) == {"myKeys": "value"}
        assert getattr(model, "keys_property") == "value"
