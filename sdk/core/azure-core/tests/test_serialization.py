# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from datetime import date, datetime, time, timedelta, tzinfo
from enum import Enum
import json
import sys
from typing import Any, Dict, List, Optional

from azure.core.serialization import AzureJSONEncoder, NULL, as_attribute_dict, is_generated_model
import pytest
from modeltypes._utils.model_base import Model as HybridModel, rest_field
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
    class Pet(HybridModel):
        name: str = rest_field()  # my name
        species: str = rest_field()  # my species

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    dict_response = {
        "name": "wall-e",
        "species": "dog",
    }
    model = Pet(
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
    # Instead of importing msrest, we're just going to do a basic rendering of the msrest models
    class MsrestModel(object):
        _subtype_map = {}
        _attribute_map = {}
        _validation = {}

        def __init__(self, *args, **kwargs):
            self.additional_properties = {}

    assert is_generated_model(MsrestModel())

    class InstantiatedMsrestModel(MsrestModel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attr = "value"

    assert is_generated_model(InstantiatedMsrestModel())


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

    class HybridAddress(HybridModel):
        street: str = rest_field()
        city: str = rest_field()
        zip_code: str = rest_field(name="zipCode")

    class HybridPerson(HybridModel):
        name: str = rest_field()
        home_address: HybridAddress = rest_field(name="homeAddress")
        work_address: HybridAddress = rest_field(name="workAddress")

    class MsrestAddress(MsrestModel):
        _attribute_map = {
            "street": {"key": "street", "type": "str"},
            "city": {"key": "city", "type": "str"},
            "zip_code": {"key": "zipCode", "type": "str"},
        }

        def __init__(self, *, street: str, city: str, zip_code: str, **kwargs):
            super().__init__(**kwargs)
            self.street = street
            self.city = city
            self.zip_code = zip_code

    class MsrestPerson(MsrestModel):
        _attribute_map = {
            "name": {"key": "name", "type": "str"},
            "home_address": {"key": "homeAddress", "type": "MsrestAddress"},
            "work_address": {"key": "workAddress", "type": "MsrestAddress"},
        }

        def __init__(self, *, name: str, home_address: MsrestAddress, work_address: MsrestAddress, **kwargs):
            super().__init__(**kwargs)
            self.name = name
            self.home_address = home_address
            self.work_address = work_address

    hybrid_home = HybridAddress(street="123 Home St", city="Hometown", zip_code="12345")
    hybrid_work = HybridAddress(street="456 Work Ave", city="Workville", zip_code="67890")
    hybrid_person = HybridPerson(name="Jane Doe", home_address=hybrid_home, work_address=hybrid_work)
    _test(as_attribute_dict(hybrid_person))
    msrest_home = MsrestAddress(street="123 Home St", city="Hometown", zip_code="12345")
    msrest_work = MsrestAddress(street="456 Work Ave", city="Workville", zip_code="67890")
    msrest_person = MsrestPerson(name="Jane Doe", home_address=msrest_home, work_address=msrest_work)
    _test(as_attribute_dict(msrest_person))


def test_as_attribute_dict_wire_name_differences():
    class HybridProduct(HybridModel):
        product_id: str = rest_field(name="productId")
        product_name: str = rest_field(name="ProductName")  # Casing difference
        unit_price: float = rest_field(name="unit-price")  # Dash in REST name
        stock_count: int = rest_field(name="stock_count")  # Underscore in both

    class MsrestProduct(MsrestModel):
        _attribute_map = {
            "product_id": {"key": "productId", "type": "str"},
            "product_name": {"key": "ProductName", "type": "str"},  # Casing difference
            "unit_price": {"key": "unit-price", "type": "float"},  # Dash in REST name
            "stock_count": {"key": "stock_count", "type": "int"},  # Underscore in both
        }

    def _test(result):
        assert result["product_id"] == "p123"
        assert result["product_name"] == "Widget"
        assert result["unit_price"] == 19.99
        assert result["stock_count"] == 42

    hybrid_product = HybridProduct(product_id="p123", product_name="Widget", unit_price=19.99, stock_count=42)
    assert hybrid_product["productId"] == "p123"
    assert hybrid_product["ProductName"] == "Widget"
    assert hybrid_product["unit-price"] == 19.99
    assert hybrid_product["stock_count"] == 42
    _test(as_attribute_dict(hybrid_product))

    msrest_product = MsrestProduct(product_id="p123", product_name="Widget", unit_price=19.99, stock_count=42)
    _test(as_attribute_dict(msrest_product))


def test_as_attribute_dict_datetime_serialization():
    class HybridEvent(HybridModel):
        event_id: str = rest_field(name="eventId")
        start_time: datetime = rest_field(name="startTime")
        end_time: datetime = rest_field(name="endTime")
        created_date: date = rest_field(name="createdDate", format="date")
        reminder_time: time = rest_field(name="reminderTime", format="time")
        duration: timedelta = rest_field(format="duration")

    class MsrestEvent(MsrestModel):
        _attribute_map = {
            "event_id": {"key": "eventId", "type": "str"},
            "start_time": {"key": "startTime", "type": "iso-8601"},
            "end_time": {"key": "endTime", "type": "iso-8601"},
            "created_date": {"key": "createdDate", "type": "date"},
            "reminder_time": {"key": "reminderTime", "type": "time"},
            "duration": {"key": "duration", "type": "duration"},
        }

        def __init__(
            self,
            *,
            event_id: str,
            start_time: datetime,
            end_time: datetime,
            created_date: date,
            reminder_time: time,
            duration: timedelta,
            **kwargs
        ):
            super().__init__(**kwargs)
            self.event_id = event_id
            self.start_time = start_time
            self.end_time = end_time
            self.created_date = created_date
            self.reminder_time = reminder_time
            self.duration = duration

    def _test(result):
        assert result["event_id"] == "e789"
        assert isinstance(result["start_time"], str)
        # TODO: chase why there are serialization diffs
        assert result["start_time"] in ["2023-05-15T09:00:00Z", "2023-05-15T09:00:00.000Z"]
        assert result["end_time"] in ["2023-05-15T10:30:00Z", "2023-05-15T10:30:00.000Z"]
        assert result["created_date"] == "2023-05-01"
        assert result["reminder_time"] == "08:45:00"
        assert result["duration"] in ["PT1H30M", "PT01H30M00S"]  # Duration can be represented in different ways

    hybrid_event = HybridEvent(
        event_id="e789",
        start_time=datetime(2023, 5, 15, 9, 0, 0),
        end_time=datetime(2023, 5, 15, 10, 30, 0),
        created_date=date(2023, 5, 1),
        reminder_time=time(8, 45, 0),
        duration=timedelta(hours=1, minutes=30),
    )
    _test(as_attribute_dict(hybrid_event))
    msrest_event = MsrestEvent(
        event_id="e789",
        start_time=datetime(2023, 5, 15, 9, 0, 0),
        end_time=datetime(2023, 5, 15, 10, 30, 0),
        created_date=date(2023, 5, 1),
        reminder_time=time(8, 45, 0),
        duration=timedelta(hours=1, minutes=30),
    )
    _test(as_attribute_dict(msrest_event))


def test_as_attribute_dict_readonly():
    class HybridResource(HybridModel):
        id: str = rest_field(visibility=["read"])  # Readonly
        name: str = rest_field()
        description: str = rest_field()

    class MsrestResource(MsrestModel):
        _validation = {
            "id": {"readonly": True},
        }
        _attribute_map = {
            "id": {"key": "id", "type": "str"},
            "name": {"key": "name", "type": "str"},
            "description": {"key": "description", "type": "str"},
        }

        def __init__(self, *, name: str, description: str, **kwargs):
            super().__init__(**kwargs)
            self.id: Optional[str] = None
            self.name = name
            self.description = description

    def _test_all(result):
        assert result["id"] == "r456"
        assert result["name"] == "My Resource"
        assert result["description"] == "A test resource"

    def _test_exclude_readonly(result):
        assert "id" not in result
        assert result["name"] == "My Resource"
        assert result["description"] == "A test resource"

    hybrid_resource = HybridResource(id="r456", name="My Resource", description="A test resource")

    # Should include all properties
    _test_all(as_attribute_dict(hybrid_resource))
    # Should exclude readonly properties
    _test_exclude_readonly(as_attribute_dict(hybrid_resource, exclude_readonly=True))

    msrest_resource = MsrestResource(name="My Resource", description="A test resource")
    msrest_resource.id = "r456"  # Manually set the readonly property for testing
    # Should include all properties
    _test_all(as_attribute_dict(msrest_resource))
    # Should exclude readonly properties
    _test_exclude_readonly(as_attribute_dict(msrest_resource, exclude_readonly=True))


def test_as_attribute_dict_collections():
    class HybridTag(HybridModel):
        key: str = rest_field()
        value: str = rest_field()

    class HybridTaggedResource(HybridModel):
        name: str = rest_field()
        tags: list[HybridTag] = rest_field()
        metadata: dict[str, str] = rest_field()
        string_list: list[str] = rest_field(name="stringList")
        int_list: list[int] = rest_field(name="intList")

    class MsrestTag(MsrestModel):
        _attribute_map = {
            "key": {"key": "key", "type": "str"},
            "value": {"key": "value", "type": "str"},
        }

        def __init__(self, *, key: str, value: str, **kwargs):
            super().__init__(**kwargs)
            self.key = key
            self.value = value

    class MsrestTaggedResource(MsrestModel):
        _attribute_map = {
            "name": {"key": "name", "type": "str"},
            "tags": {"key": "tags", "type": "[MsrestTag]"},
            "metadata": {"key": "metadata", "type": "{str}"},
            "string_list": {"key": "stringList", "type": "[str]"},
            "int_list": {"key": "intList", "type": "[int]"},
        }

        def __init__(
            self,
            *,
            name: str,
            tags: List[MsrestTag],
            metadata: Dict[str, str],
            string_list: List[str],
            int_list: List[int],
            **kwargs
        ):
            super().__init__(**kwargs)
            self.name = name
            self.tags = tags
            self.metadata = metadata
            self.string_list = string_list
            self.int_list = int_list

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

    hybrid_tags = [HybridTag(key="env", value="prod"), HybridTag(key="dept", value="finance")]
    hybrid_resource = HybridTaggedResource(
        name="Tagged Resource",
        tags=hybrid_tags,
        metadata={"created_by": "admin", "priority": "high"},
        string_list=["a", "b", "c"],
        int_list=[1, 2, 3],
    )
    _test(as_attribute_dict(hybrid_resource))

    msrest_tags = [MsrestTag(key="env", value="prod"), MsrestTag(key="dept", value="finance")]
    msrest_resource = MsrestTaggedResource(
        name="Tagged Resource",
        tags=msrest_tags,
        metadata={"created_by": "admin", "priority": "high"},
        string_list=["a", "b", "c"],
        int_list=[1, 2, 3],
    )
    _test(as_attribute_dict(msrest_resource))


def test_as_attribute_dict_inheritance():
    class HybridBaseModel(HybridModel):
        id: str = rest_field()
        type: str = rest_field()

    class HybridPet(HybridBaseModel):
        name: str = rest_field()
        age: int = rest_field()

    class HybridDog(HybridPet):
        breed: str = rest_field()
        is_best_boy: bool = rest_field(name="isBestBoy")

    class MsrestBaseModel(MsrestModel):
        _attribute_map = {
            "id": {"key": "id", "type": "str"},
            "type": {"key": "type", "type": "str"},
        }

        def __init__(self, *, id: str, type: str, **kwargs):
            super().__init__(**kwargs)
            self.id = id
            self.type = type

    class MsrestPet(MsrestBaseModel):
        _attribute_map = {
            "id": {"key": "id", "type": "str"},
            "type": {"key": "type", "type": "str"},
            "name": {"key": "name", "type": "str"},
            "age": {"key": "age", "type": "int"},
        }

        def __init__(self, *, id: str, type: str, name: str, age: int, **kwargs):
            super().__init__(id=id, type=type, **kwargs)
            self.name = name
            self.age = age

    class MsrestDog(MsrestPet):
        _attribute_map = {
            "id": {"key": "id", "type": "str"},
            "type": {"key": "type", "type": "str"},
            "name": {"key": "name", "type": "str"},
            "age": {"key": "age", "type": "int"},
            "breed": {"key": "breed", "type": "str"},
            "is_best_boy": {"key": "isBestBoy", "type": "bool"},
        }

        def __init__(self, *, id: str, type: str, name: str, age: int, breed: str, is_best_boy: bool, **kwargs):
            super().__init__(id=id, type=type, name=name, age=age, **kwargs)
            self.breed = breed
            self.is_best_boy = is_best_boy

    def _test(result):
        assert result["id"] == "d123"
        assert result["type"] == "dog"
        assert result["name"] == "Wall-E"
        assert result["age"] == 2
        assert result["breed"] == "Pitbull"
        assert result["is_best_boy"] is True

    hybrid_dog = HybridDog(id="d123", type="dog", name="Wall-E", age=2, breed="Pitbull", is_best_boy=True)

    _test(as_attribute_dict(hybrid_dog))

    msrest_dog = MsrestDog(id="d123", type="dog", name="Wall-E", age=2, breed="Pitbull", is_best_boy=True)
    _test(as_attribute_dict(msrest_dog))


def test_as_attribute_dict_multipart_file():
    from typing import BinaryIO
    from io import BytesIO

    class FileUpload(HybridModel):
        name: str = rest_field()
        content: BinaryIO = rest_field(is_multipart_file_input=True)
        content_type: str = rest_field(name="contentType")

    file_data = BytesIO(b"This is test file content")
    upload = FileUpload(name="test.txt", content=file_data, content_type="text/plain")

    attr_dict = as_attribute_dict(upload)
    assert attr_dict["name"] == "test.txt"
    assert attr_dict["content"] is file_data  # Should be preserved as-is for multipart files
    assert attr_dict["content_type"] == "text/plain"


def test_as_attribute_dict_with_null_object():
    class HybridOptionalProps(HybridModel):
        required_prop: str = rest_field()
        optional_prop: Optional[str] = rest_field(name="optionalProp")
        optional_model: Optional["HybridOptionalProps"] = rest_field(name="optionalModel")

    class MsrestOptionalProps(MsrestModel):
        _attribute_map = {
            "required_prop": {"key": "requiredProp", "type": "str"},
            "optional_prop": {"key": "optionalProp", "type": "str"},
            "optional_model": {"key": "optionalModel", "type": "HybridOptionalProps"},
        }

        def __init__(
            self,
            *,
            required_prop: str,
            optional_prop: Optional[str] = None,
            optional_model: Optional["HybridOptionalProps"] = None,
            **kwargs
        ):
            super().__init__(**kwargs)
            self.required_prop = required_prop
            self.optional_prop = optional_prop
            self.optional_model = optional_model

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

    hybrid_model = HybridOptionalProps(required_prop="always here", optional_prop=None, optional_model=None)

    _test_non_nested(as_attribute_dict(hybrid_model))

    msrest_model = MsrestOptionalProps(required_prop="always here", optional_prop=None, optional_model=None)
    _test_non_nested(as_attribute_dict(msrest_model))

    # Test with a nested model that has a null property
    hybrid_nested = HybridOptionalProps(required_prop="nested", optional_prop="present", optional_model=None)
    hybrid_model = HybridOptionalProps(required_prop="outer", optional_prop=None, optional_model=hybrid_nested)

    _test_nested(as_attribute_dict(hybrid_model))

    msrest_nested = MsrestOptionalProps(required_prop="nested", optional_prop="present", optional_model=None)
    msrest_model = MsrestOptionalProps(required_prop="outer", optional_prop=None, optional_model=msrest_nested)
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
    class HybridAddress(HybridModel):
        street: str = rest_field(name="streetAddress")
        city: str = rest_field()
        postal_code: str = rest_field(name="postalCode")

    class HybridContactInfo(HybridModel):
        email: str = rest_field()
        phone: str = rest_field()
        addresses: List[HybridAddress] = rest_field()

    class HybridDepartment(HybridModel):
        name: str = rest_field()
        cost_center: str = rest_field(name="costCenter")

    class HybridEmployee(HybridModel):
        employee_id: str = rest_field(name="employeeId", visibility=["read"])
        first_name: str = rest_field(name="firstName")
        last_name: str = rest_field(name="lastName")
        hire_date: date = rest_field(name="hireDate")
        contact: HybridContactInfo = rest_field()
        department: HybridDepartment = rest_field()
        skills: List[str] = rest_field()
        performance_ratings: dict[str, float] = rest_field(name="performanceRatings")

    class MsrestAddress(MsrestModel):
        _attribute_map = {
            "street": {"key": "streetAddress", "type": "str"},
            "city": {"key": "city", "type": "str"},
            "postal_code": {"key": "postalCode", "type": "str"},
        }

        def __init__(self, *, street: str, city: str, postal_code: str, **kwargs):
            super().__init__(**kwargs)
            self.street = street
            self.city = city
            self.postal_code = postal_code

    class MsrestContactInfo(MsrestModel):
        _attribute_map = {
            "email": {"key": "email", "type": "str"},
            "phone": {"key": "phone", "type": "str"},
            "addresses": {"key": "addresses", "type": "[MsrestAddress]"},
        }

        def __init__(self, *, email: str, phone: str, addresses: List[MsrestAddress], **kwargs):
            super().__init__(**kwargs)
            self.email = email
            self.phone = phone
            self.addresses = addresses

    class MsrestDepartment(MsrestModel):
        _attribute_map = {
            "name": {"key": "name", "type": "str"},
            "cost_center": {"key": "costCenter", "type": "str"},
        }

        def __init__(self, *, name: str, cost_center: str, **kwargs):
            super().__init__(**kwargs)
            self.name = name
            self.cost_center = cost_center

    class MsrestEmployee(MsrestModel):

        _validation = {
            "employee_id": {"readonly": True},
        }
        _attribute_map = {
            "employee_id": {"key": "employeeId", "type": "str"},
            "first_name": {"key": "firstName", "type": "str"},
            "last_name": {"key": "lastName", "type": "str"},
            "hire_date": {"key": "hireDate", "type": "date"},
            "contact": {"key": "contact", "type": "MsrestContactInfo"},
            "department": {"key": "department", "type": "MsrestDepartment"},
            "skills": {"key": "skills", "type": "[str]"},
            "performance_ratings": {"key": "performanceRatings", "type": "{str: float}"},
        }

        def __init__(
            self,
            *,
            employee_id: str,
            first_name: str,
            last_name: str,
            hire_date: date,
            contact: MsrestContactInfo,
            department: MsrestDepartment,
            skills: List[str],
            performance_ratings: Dict[str, float],
            **kwargs
        ):
            super().__init__(**kwargs)
            self.employee_id = employee_id
            self.first_name = first_name
            self.last_name = last_name
            self.hire_date = hire_date
            self.contact = contact
            self.department = department
            self.skills = skills
            self.performance_ratings = performance_ratings

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
        assert result["contact"]["addresses"][0]["postal_code"] == "12345"

        # Verify department
        assert result["department"]["name"] == "Engineering"
        assert result["department"]["cost_center"] == "CC-ENG-123"

        # Verify collections
        assert result["skills"] == ["Python", "TypeScript", "Azure"]
        assert result["performance_ratings"] == {"2020": 4.5, "2021": 4.7, "2022": 4.8}

    # Create a complex employee object
    hybrid_employee = HybridEmployee(
        employee_id="E12345",
        first_name="Jane",
        last_name="Doe",
        hire_date=date(2020, 3, 15),
        contact=HybridContactInfo(
            email="jane.doe@example.com",
            phone="555-123-4567",
            addresses=[
                HybridAddress(street="123 Home St", city="Hometown", postal_code="12345"),
                HybridAddress(street="456 Work Ave", city="Workville", postal_code="67890"),
            ],
        ),
        department=HybridDepartment(name="Engineering", cost_center="CC-ENG-123"),
        skills=["Python", "TypeScript", "Azure"],
        performance_ratings={"2020": 4.5, "2021": 4.7, "2022": 4.8},
    )

    # Get full attribute dictionary
    _test(as_attribute_dict(hybrid_employee))

    # Now check with exclude_readonly=True
    attr_dict = as_attribute_dict(hybrid_employee, exclude_readonly=True)
    assert "employee_id" not in attr_dict
    assert attr_dict["first_name"] == "Jane"

    msrest_employee = MsrestEmployee(
        employee_id="E12345",
        first_name="Jane",
        last_name="Doe",
        hire_date=date(2020, 3, 15),
        contact=MsrestContactInfo(
            email="jane.doe@example.com",
            phone="555-123-4567",
            addresses=[
                MsrestAddress(street="123 Home St", city="Hometown", postal_code="12345"),
                MsrestAddress(street="456 Work Ave", city="Workville", postal_code="67890"),
            ],
        ),
        department=MsrestDepartment(name="Engineering", cost_center="CC-ENG-123"),
        skills=["Python", "TypeScript", "Azure"],
        performance_ratings={"2020": 4.5, "2021": 4.7, "2022": 4.8},
    )

    _test(as_attribute_dict(msrest_employee))
    # Now check with exclude_readonly=True
    attr_dict = as_attribute_dict(msrest_employee, exclude_readonly=True)
    assert "employee_id" not in attr_dict
    assert attr_dict["first_name"] == "Jane"


def test_as_attribute_dict_flatten():
    class MsrestFlattenModel(MsrestModel):
        _attribute_map = {
            "name": {"key": "name", "type": "str"},
            "description": {"key": "properties.modelDescription", "type": "str"},
            "age": {"key": "properties.age", "type": "int"},
        }

        def __init__(self, *, name: str, description: str, age: int, **kwargs):
            super().__init__(**kwargs)
            self.name = name
            self.description = description
            self.age = age

    def _test(result):
        assert result["name"] == "wall-e"
        assert result["description"] == "a dog"
        assert result["age"] == 2
        assert "properties" not in result
        assert "modelDescription" not in result
        assert "model_description" not in result

    hybrid_model = models.FlattenModel(name="wall-e", description="a dog", age=2)
    msrest_model = MsrestFlattenModel(name="wall-e", description="a dog", age=2)

    _test(as_attribute_dict(hybrid_model))
    _test(as_attribute_dict(msrest_model))


def test_as_attribute_dict_additional_properties():
    class HybridPetAPTrue(HybridModel):
        name: str = rest_field()

    class MsrestPetAPTrue(MsrestModel):
        _attribute_map = {
            "additional_properties": {"key": "", "type": "{object}"},
            "name": {"key": "name", "type": "str"},
        }

        def __init__(self, *, additional_properties: Optional[Dict[str, Any]], name: Optional[str] = None, **kwargs):
            super().__init__(**kwargs)
            self.additional_properties = additional_properties
            self.name = name

    def _tests(model):
        attr_dict = as_attribute_dict(model)
        assert attr_dict["name"] == "Buddy"
        assert "additional_properties" not in attr_dict
        assert attr_dict["birthdate"] == "2017-12-13T02:29:51Z"
        assert attr_dict["complexProperty"] == {"color": "Red"}
        assert getattr(model, "birthdate", None) is None
        assert getattr(model, "complexProperty", None) is None

    hybrid_model = HybridPetAPTrue(
        {"birthdate": "2017-12-13T02:29:51Z", "complexProperty": {"color": "Red"}, "name": "Buddy"}
    )
    assert getattr(hybrid_model, "additional_properties", None) is None
    _tests(hybrid_model)
    msrest_model = MsrestPetAPTrue(
        additional_properties={"birthdate": "2017-12-13T02:29:51Z", "complexProperty": {"color": "Red"}}, name="Buddy"
    )
    _tests(msrest_model)
    assert msrest_model.additional_properties == {
        "birthdate": "2017-12-13T02:29:51Z",
        "complexProperty": {"color": "Red"},
    }
