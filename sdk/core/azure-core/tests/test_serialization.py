# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from datetime import date, datetime, time, timedelta, tzinfo
from enum import Enum
import json
import sys

from azure.core.serialization import AzureJSONEncoder, NULL, as_attribute_dict
import pytest
from modeltypes._utils.model_base import Model as HybridModel, rest_field
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
    def _flattened_model_assertions(model):
        assert model.name == "wall-e"
        assert model.description == "a dog"
        assert model.age == 2
        assert model.properties.description == "a dog"
        assert model.properties.age == 2

    model = models.FlattenModel(name="wall-e", description="a dog", age=2)
    _flattened_model_assertions(model)
    model = models.FlattenModel({"name": "wall-e", "properties": {"description": "a dog", "age": 2}})
    _flattened_model_assertions(model)


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

def test_as_attribute_dict_client_name():
    model = models.ClientNameAndJsonEncodedNameModel(client_name="wall-e")
    assert model.as_dict() == {"wireName": "wall-e"}
    assert as_attribute_dict(model) == {"client_name": "wall-e"}

def test_as_attribute_dict_nested_models():
    class Address(HybridModel):
        street: str = rest_field()
        city: str = rest_field()
        zip_code: str = rest_field(name="zipCode")
        
    class Person(HybridModel):
        name: str = rest_field()
        home_address: Address = rest_field(name="homeAddress")
        work_address: Address = rest_field(name="workAddress")
        
    home = Address(street="123 Home St", city="Hometown", zip_code="12345")
    work = Address(street="456 Work Ave", city="Workville", zip_code="67890")
    person = Person(name="Jane Doe", home_address=home, work_address=work)
    
    result = as_attribute_dict(person)

    assert result["name"] == "Jane Doe"
    assert result["home_address"]["street"] == "123 Home St"
    assert result["home_address"]["city"] == "Hometown"
    assert result["home_address"]["zip_code"] == "12345"
    assert result["work_address"]["street"] == "456 Work Ave"
    assert result["work_address"]["city"] == "Workville"
    assert result["work_address"]["zip_code"] == "67890"

def test_as_attribute_dict_wire_name_differences():
    class Product(HybridModel):
        product_id: str = rest_field(name="productId")
        product_name: str = rest_field(name="ProductName")  # Casing difference
        unit_price: float = rest_field(name="unit-price")  # Dash in REST name
        stock_count: int = rest_field(name="stock_count")  # Underscore in both
        
    product = Product(
        product_id="p123",
        product_name="Widget",
        unit_price=19.99,
        stock_count=42
    )

    assert product["productId"] == "p123"
    assert product["ProductName"] == "Widget"
    assert product["unit-price"] == 19.99
    assert product["stock_count"] == 42
    
    attr_dict = as_attribute_dict(product)
    assert attr_dict["product_id"] == "p123"
    assert attr_dict["product_name"] == "Widget"
    assert attr_dict["unit_price"] == 19.99
    assert attr_dict["stock_count"] == 42

def test_as_attribute_dict_datetime_serialization():
    class Event(HybridModel):
        event_id: str = rest_field(name="eventId")
        start_time: datetime = rest_field(name="startTime")
        end_time: datetime = rest_field(name="endTime")
        created_date: date = rest_field(name="createdDate")
        reminder_time: time = rest_field(name="reminderTime")
        duration: timedelta = rest_field()
        
    event = Event(
        event_id="e789",
        start_time=datetime(2023, 5, 15, 9, 0, 0),
        end_time=datetime(2023, 5, 15, 10, 30, 0),
        created_date=date(2023, 5, 1),
        reminder_time=time(8, 45, 0),
        duration=timedelta(hours=1, minutes=30)
    )
    
    attr_dict = as_attribute_dict(event)
    assert attr_dict["event_id"] == "e789"
    assert isinstance(attr_dict["start_time"], str)
    assert attr_dict["start_time"] == "2023-05-15T09:00:00Z"
    assert attr_dict["end_time"] == "2023-05-15T10:30:00Z"
    assert attr_dict["created_date"] == "2023-05-01"
    assert attr_dict["reminder_time"] == "08:45:00"
    assert attr_dict["duration"] == "PT01H30M00S"  # ISO 8601 format for timedelta

def test_as_attribute_dict_readonly():
    class Resource(HybridModel):
        id: str = rest_field(visibility=["read"])  # Readonly
        name: str = rest_field()
        created_at: datetime = rest_field(name="createdAt", visibility=["read"])  # Readonly
        updated_at: datetime = rest_field(name="updatedAt", visibility=["read"])  # Readonly
        description: str = rest_field()
        
    resource = Resource(
        id="r456",
        name="My Resource",
        created_at=datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime(2023, 2, 1, 14, 30, 0),
        description="A test resource"
    )
    
    # Should include all properties
    attr_dict = as_attribute_dict(resource)
    assert attr_dict["id"] == "r456"
    assert attr_dict["name"] == "My Resource"
    assert attr_dict["created_at"] == "2023-01-01T12:00:00Z"
    assert attr_dict["updated_at"] == "2023-02-01T14:30:00Z"
    assert attr_dict["description"] == "A test resource"
    
    # Should exclude readonly properties
    attr_dict = as_attribute_dict(resource, exclude_readonly=True)
    assert "id" not in attr_dict
    assert attr_dict["name"] == "My Resource"
    assert "created_at" not in attr_dict
    assert "updated_at" not in attr_dict
    assert attr_dict["description"] == "A test resource"

def test_as_attribute_dict_collections():
    class Tag(HybridModel):
        key: str = rest_field()
        value: str = rest_field()
        
    class TaggedResource(HybridModel):
        name: str = rest_field()
        tags: list[Tag] = rest_field()
        metadata: dict[str, str] = rest_field()
        string_list: list[str] = rest_field(name="stringList")
        int_list: list[int] = rest_field(name="intList")
        
    tags = [Tag(key="env", value="prod"), Tag(key="dept", value="finance")]
    resource = TaggedResource(
        name="Tagged Resource",
        tags=tags,
        metadata={"created_by": "admin", "priority": "high"},
        string_list=["a", "b", "c"],
        int_list=[1, 2, 3]
    )
    
    attr_dict = as_attribute_dict(resource)
    assert attr_dict["name"] == "Tagged Resource"
    assert isinstance(attr_dict["tags"], list)
    assert len(attr_dict["tags"]) == 2
    assert attr_dict["tags"][0]["key"] == "env"
    assert attr_dict["tags"][0]["value"] == "prod"
    assert attr_dict["tags"][1]["key"] == "dept"
    assert attr_dict["tags"][1]["value"] == "finance"
    assert attr_dict["metadata"] == {"created_by": "admin", "priority": "high"}
    assert attr_dict["string_list"] == ["a", "b", "c"]
    assert attr_dict["int_list"] == [1, 2, 3]

def test_as_attribute_dict_inheritance():
    class BaseModel(HybridModel):
        id: str = rest_field()
        type: str = rest_field()
        
    class Pet(BaseModel):
        name: str = rest_field()
        age: int = rest_field()
        
    class Dog(Pet):
        breed: str = rest_field()
        is_best_boy: bool = rest_field(name="isBestBoy")

    dog = Dog(
        id="d123",
        type="dog",
        name="Wall-E",
        age=2,
        breed="Pitbull",
        is_best_boy=True
    )
    
    attr_dict = as_attribute_dict(dog)
    assert attr_dict["id"] == "d123"
    assert attr_dict["type"] == "dog"
    assert attr_dict["name"] == "Wall-E"
    assert attr_dict["age"] == 2
    assert attr_dict["breed"] == "Pitbull"
    assert attr_dict["is_best_boy"] == True

def test_as_attribute_dict_multipart_file():
    from typing import BinaryIO
    from io import BytesIO
    
    class FileUpload(HybridModel):
        name: str = rest_field()
        content: BinaryIO = rest_field(is_multipart_file_input=True)
        content_type: str = rest_field(name="contentType")
        
    file_data = BytesIO(b"This is test file content")
    upload = FileUpload(
        name="test.txt",
        content=file_data,
        content_type="text/plain"
    )
    
    attr_dict = as_attribute_dict(upload)
    assert attr_dict["name"] == "test.txt"
    assert attr_dict["content"] is file_data  # Should be preserved as-is for multipart files
    assert attr_dict["content_type"] == "text/plain"

def test_as_attribute_dict_with_null_object():
    class OptionalProps(HybridModel):
        required_prop: str = rest_field()
        optional_prop: str = rest_field()
        optional_model: 'OptionalProps' = rest_field()
        
    model = OptionalProps(
        required_prop="always here",
        optional_prop=None,
        optional_model=None
    )
    
    attr_dict = as_attribute_dict(model)
    assert attr_dict["required_prop"] == "always here"
    assert attr_dict["optional_prop"] is None
    assert attr_dict["optional_model"] is None
    
    # Test with a nested model that has a null property
    nested = OptionalProps(
        required_prop="nested",
        optional_prop="present", 
        optional_model=None
    )
    model = OptionalProps(
        required_prop="outer",
        optional_prop=None,
        optional_model=nested
    )
    
    attr_dict = as_attribute_dict(model)
    assert attr_dict["required_prop"] == "outer"
    assert attr_dict["optional_prop"] is None
    assert attr_dict["optional_model"]["required_prop"] == "nested"
    assert attr_dict["optional_model"]["optional_prop"] == "present"
    assert attr_dict["optional_model"]["optional_model"] is None

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
    class Address(HybridModel):
        street: str = rest_field(name="streetAddress")
        city: str = rest_field()
        postal_code: str = rest_field(name="postalCode")
        
    class ContactInfo(HybridModel):
        email: str = rest_field()
        phone: str = rest_field()
        addresses: list[Address] = rest_field()
        
    class Department(HybridModel):
        name: str = rest_field()
        cost_center: str = rest_field(name="costCenter")
        
    class Employee(HybridModel):
        employee_id: str = rest_field(name="employeeId", visibility=["read"])
        first_name: str = rest_field(name="firstName")
        last_name: str = rest_field(name="lastName")
        hire_date: date = rest_field(name="hireDate")
        contact: ContactInfo = rest_field()
        department: Department = rest_field()
        skills: list[str] = rest_field()
        performance_ratings: dict[str, float] = rest_field(name="performanceRatings")
        
    # Create a complex employee object
    employee = Employee(
        employee_id="E12345",
        first_name="Jane",
        last_name="Doe",
        hire_date=date(2020, 3, 15),
        contact=ContactInfo(
            email="jane.doe@example.com",
            phone="555-123-4567",
            addresses=[
                Address(street="123 Home St", city="Hometown", postal_code="12345"),
                Address(street="456 Work Ave", city="Workville", postal_code="67890")
            ]
        ),
        department=Department(
            name="Engineering",
            cost_center="CC-ENG-123"
        ),
        skills=["Python", "TypeScript", "Azure"],
        performance_ratings={
            "2020": 4.5,
            "2021": 4.7, 
            "2022": 4.8
        }
    )
    
    # Get full attribute dictionary
    attr_dict = as_attribute_dict(employee)
    
    # Verify top-level properties
    assert attr_dict["employee_id"] == "E12345"
    assert attr_dict["first_name"] == "Jane"
    assert attr_dict["last_name"] == "Doe"
    assert attr_dict["hire_date"] == '2020-03-15'
    
    # Verify nested contact info
    assert attr_dict["contact"]["email"] == "jane.doe@example.com"
    assert attr_dict["contact"]["phone"] == "555-123-4567"
    
    # Verify list of address objects
    assert len(attr_dict["contact"]["addresses"]) == 2
    assert attr_dict["contact"]["addresses"][0]["street"] == "123 Home St"
    assert attr_dict["contact"]["addresses"][0]["city"] == "Hometown"
    assert attr_dict["contact"]["addresses"][0]["postal_code"] == "12345"
    
    # Verify department
    assert attr_dict["department"]["name"] == "Engineering"
    assert attr_dict["department"]["cost_center"] == "CC-ENG-123"
    
    # Verify collections
    assert attr_dict["skills"] == ["Python", "TypeScript", "Azure"]
    assert attr_dict["performance_ratings"] == {"2020": 4.5, "2021": 4.7, "2022": 4.8}
    
    # Now check with exclude_readonly=True
    attr_dict = as_attribute_dict(employee, exclude_readonly=True)
    assert "employee_id" not in attr_dict
    assert attr_dict["first_name"] == "Jane"
