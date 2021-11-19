# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import datetime
from typing import Any, List, Literal, Dict, Set, Tuple, Optional
import pytest
import isodate
from azure.core.serialization import Model, rest_property

def modify_args(init):
    def _wrapper(self, **kwargs):
        init(self, **{
            self._get_property_name(kwarg) or kwarg: value
            for kwarg, value in kwargs.items()
        })
    return _wrapper


class BasicResource(Model):

    @rest_property(name="platformUpdateDomainCount")
    def platform_update_domain_count(self) -> int:
        """How many times the platform update domain has been counted"""

    @rest_property(name="platformFaultDomainCount")
    def platform_fault_domain_count(self) -> int:
        """How many times the platform fault domain has been counted"""

    @rest_property(name="virtualMachines")
    def virtual_machines(self) -> List[Any]:
        """List of virtual machines"""


def test_model_and_dict_equal():

    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    model = BasicResource(dict_response)
    model.platform_update_domain_count
    assert model == dict_response
    assert (
        model.platform_update_domain_count ==
        model["platformUpdateDomainCount"] ==
        dict_response["platformUpdateDomainCount"] ==
        5
    )
    assert (
        model.platform_fault_domain_count ==
        model['platformFaultDomainCount'] ==
        dict_response['platformFaultDomainCount'] ==
        3
    )
    assert (
        model.virtual_machines ==
        model['virtualMachines'] ==
        dict_response['virtualMachines'] ==
        []
    )

def test_model_initialization():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    a = BasicResource(platformUpdateDomainCount=5, platformFaultDomainCount=3, virtualMachines=[])
    b = BasicResource(zip(['platformUpdateDomainCount', 'platformFaultDomainCount', 'virtualMachines'], [5, 3, []]))
    c = BasicResource([('platformFaultDomainCount', 3), ('platformUpdateDomainCount', 5), ('virtualMachines', [])])
    d = BasicResource({'virtualMachines': [], 'platformFaultDomainCount': 3, 'platformUpdateDomainCount': 5})
    e = BasicResource({'platformFaultDomainCount': 3, 'virtualMachines': []}, platformUpdateDomainCount=5)
    f = BasicResource(dict_response)
    g = BasicResource(**dict_response)
    assert a == b == c == d == e == f == g
    dicts = [a, b, c, d, e, f, g]
    for d in dicts:
        assert len(d) == 3
        assert d['platformUpdateDomainCount'] == d.platform_update_domain_count == 5
        assert d['platformFaultDomainCount'] == d.platform_fault_domain_count == 3
        assert d['virtualMachines'] == d.virtual_machines == []

def test_json_roundtrip():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    model = BasicResource(dict_response)
    assert json.dumps(model) == '{"platformUpdateDomainCount": 5, "platformFaultDomainCount": 3, "virtualMachines": []}'
    assert json.loads(json.dumps(model)) == model == dict_response

def test_has_no_property():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": [],
        "noprop": "bonjour!"
    }
    model = BasicResource(dict_response)
    assert (
        model.platform_update_domain_count ==
        model["platformUpdateDomainCount"] ==
        dict_response["platformUpdateDomainCount"] ==
        5
    )
    assert not hasattr(model, "no_prop")
    with pytest.raises(AttributeError) as ex:
        model.no_prop

    assert str(ex.value) == "'BasicResource' object has no attribute 'no_prop'"
    assert model["noprop"] == dict_response["noprop"] == "bonjour!"

    # let's add it to model now

    class BasicResourceWithProperty(BasicResource):

        @rest_property(name="noprop")
        def no_prop(self) -> str:
            """Added prop"""

    model = BasicResourceWithProperty(dict_response)
    model.no_prop
    assert (
        model.no_prop ==
        model["noprop"] ==
        dict_response["noprop"] ==
        "bonjour!"
    )

def test_original_and_attr_name_same():

    class MyModel(Model):
        @rest_property()
        def hello(self) -> str:
            """Prop with the same attr and dict name"""

    dict_response = {"hello": "nihao"}
    model = MyModel(dict_response)
    assert model.hello == model["hello"] == dict_response["hello"]

def test_optional_property():

    class MyModel(Model):

        @rest_property()
        def optional_str(self) -> Optional[str]:
            """optional string property"""

        @rest_property()
        def optional_time(self) -> Optional[datetime.time]:
            """optional time property"""

def test_modify_dict():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    model = BasicResource(**dict_response)

    # now let's modify the model as a dict
    model["platformUpdateDomainCount"] = 100
    assert model.platform_update_domain_count == model["platformUpdateDomainCount"] == 100

def test_modify_property():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    model = BasicResource(**dict_response)

    # now let's modify the model through it's properties
    model.platform_fault_domain_count = 2000
    model['platformFaultDomainCount']
    assert model.platform_fault_domain_count == model["platformFaultDomainCount"] == 2000

def test_property_is_a_type():
    class Fish(Model):

        @rest_property()
        def name(self) -> str:
            """My Fish name"""

        @rest_property()
        def species(self) -> Literal['Salmon', 'Halibut']:
            """My species"""

    class Fishery(Model):

        @rest_property()
        def fish(self) -> Fish:
            """The fish in my fishery."""

    fishery = Fishery({"fish": {"name": "Benjamin", "species": "Salmon"}})
    assert isinstance(fishery.fish, Fish)
    assert fishery.fish.name == fishery.fish['name'] == fishery['fish']['name'] == "Benjamin"
    assert fishery.fish.species == fishery.fish['species'] == fishery['fish']['species'] == "Salmon"

def test_datetime_deserialization():
    class DatetimeModel(Model):

        @rest_property(name="datetimeValue")
        def datetime_value(self) -> datetime.datetime:
            """My datetime Value"""

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    model = DatetimeModel({"datetimeValue": val_str})
    assert model['datetimeValue'] == val_str
    assert model.datetime_value == val

    class BaseModel(Model):

        @rest_property(name="myProp")
        def my_prop(self) -> DatetimeModel:
            """My property, which is an instance of DatetimeModel"""

    model = BaseModel({"myProp": {"datetimeValue": val_str}})
    assert isinstance(model.my_prop, DatetimeModel)
    assert model.my_prop['datetimeValue'] == model['myProp']['datetimeValue'] == val_str
    assert model.my_prop.datetime_value == val

def test_date_deserialization():
    class DateModel(Model):

        @rest_property(name="dateValue")
        def date_value(self) -> datetime.date:
            """My date value"""

    val_str = "2016-02-29"
    val = isodate.parse_date(val_str)
    model = DateModel({"dateValue": val_str})
    assert model['dateValue'] == val_str
    assert model.date_value == val

    class BaseModel(Model):

        @rest_property(name="myProp")
        def my_prop(self) -> DateModel:
            """My property, which is an instance of DateModel"""

    model = BaseModel({"myProp": {"dateValue": val_str}})
    assert isinstance(model.my_prop, DateModel)
    assert model.my_prop['dateValue'] == model['myProp']['dateValue'] == val_str
    assert model.my_prop.date_value == val

def test_time_deserialization():
    class TimeModel(Model):

        @rest_property(name="timeValue")
        def time_value(self) -> datetime.time:
            """My time value"""

    val_str = '11:34:56'
    val = datetime.time(11, 34, 56)
    model = TimeModel({"timeValue": val_str})
    assert model['timeValue'] == val_str
    assert model.time_value == val

    class BaseModel(Model):

        @rest_property(name="myProp")
        def my_prop(self) -> TimeModel:
            """My property, which is an instance of TimeModel"""

    model = BaseModel({"myProp": {"timeValue": val_str}})
    assert isinstance(model.my_prop, TimeModel)
    assert model.my_prop['timeValue'] == model['myProp']['timeValue'] == val_str
    assert model.my_prop.time_value == val

class RecursiveModel(Model):

    @rest_property()
    def name(self) -> str:
        """My name."""

    @rest_property()
    def me(self) -> "RecursiveModel":
        """Me!"""

def test_model_recursion():

    dict_response = {
        "name": "Snoopy",
        "me": {
            "name": "Egg",
            "me": {
                "name": "Chicken"
            }
        }
    }

    model = RecursiveModel(dict_response)
    assert model['name'] == model.name == "Snoopy"
    assert model['me'] == {
        "name": "Egg",
        "me": {
            "name": "Chicken"
        }
    }
    assert isinstance(model.me, RecursiveModel)
    assert model.me['name'] == model.me.name == "Egg"
    assert model.me['me'] == {"name": "Chicken"}
    assert model.me.me.name == "Chicken"

def test_dictionary_deserialization():
    class DictionaryModel(Model):

        @rest_property()
        def prop(self) -> Dict[str, datetime.datetime]:
            """Dictionary of str to datetime.datetime"""

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    dict_response = {
        "prop": {
            "datetime": val_str
        }
    }
    model = DictionaryModel(dict_response)
    assert model['prop'] == {"datetime": val_str}
    assert model.prop == {"datetime": val}

def test_list_deserialization():
    class ListModel(Model):

        @rest_property()
        def prop(self) -> List[datetime.datetime]:
            """Dictionary of str to datetime.datetime"""

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    dict_response = {
        "prop": [val_str, val_str]
    }
    model = ListModel(dict_response)
    assert model['prop'] == [val_str, val_str]
    assert model.prop == [val, val]

def test_set_deserialization():
    class SetModel(Model):

        @rest_property()
        def prop(self) -> Set[datetime.datetime]:
            """Dictionary of str to datetime.datetime"""

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    dict_response = {
        "prop": set([val_str, val_str])
    }
    model = SetModel(dict_response)
    assert model['prop'] == set([val_str, val_str])
    assert model.prop == set([val, val])

def test_tuple_deserialization():
    class TupleModel(Model):

        @rest_property()
        def prop(self) -> Tuple[str, datetime.datetime]:
            """Dictionary of str to datetime.datetime"""

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    dict_response = {
        "prop": (val_str, val_str)
    }
    model = TupleModel(dict_response)
    assert model['prop'] == (val_str, val_str)
    assert model.prop == (val_str, val)

def test_model_recursion_complex():
    class RecursiveModel(Model):

        @rest_property()
        def name(self) -> str:
            """My name"""

        @rest_property(name="listOfMe")
        def list_of_me(self) -> List["RecursiveModel"]:
            """A list of myself"""

        @rest_property(name="dictOfMe")
        def dict_of_me(self) -> Dict[str, "RecursiveModel"]:
            """A dictionary of me"""

        @rest_property(name="dictOfListOfMe")
        def dict_of_list_of_me(self) -> Dict[str, List["RecursiveModel"]]:
            """A dictionary of a list of me"""

        @rest_property(name="listOfDictOfMe")
        def list_of_dict_of_me(self) -> List[Dict[str, "RecursiveModel"]]:
            """A list of a dictionary of me"""

    dict_response = {
        "name": "it's me!",
        "listOfMe": [
            {
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None
            }
        ],
        "dictOfMe": {
            "me": {
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None
            }
        },
        "dictOfListOfMe": {
            "many mes": [
                {
                    "name": "it's me!",
                    "listOfMe": None,
                    "dictOfMe": None,
                    "dictOfListOfMe": None,
                    "listOfDictOfMe": None
                }
            ]
        },
        "listOfDictOfMe": [
            {"me": {
                    "name": "it's me!",
                    "listOfMe": None,
                    "dictOfMe": None,
                    "dictOfListOfMe": None,
                    "listOfDictOfMe": None
                }
            }
        ]
    }

    model = RecursiveModel(dict_response)
    assert model.name == model['name'] == "it's me!"
    assert model['listOfMe'] == [
        {
            "name": "it's me!",
            "listOfMe": None,
            "dictOfMe": None,
            "dictOfListOfMe": None,
            "listOfDictOfMe": None
        }
    ]
    assert model.list_of_me == [RecursiveModel({
        "name": "it's me!",
        "listOfMe": None,
        "dictOfMe": None,
        "dictOfListOfMe": None,
        "listOfDictOfMe": None
    })]
    assert model.list_of_me[0].name == "it's me!"
    assert model.list_of_me[0].list_of_me

    assert model['dictOfMe'] == {
        "me": {
            "name": "it's me!",
            "listOfMe": None,
            "dictOfMe": None,
            "dictOfListOfMe": None,
            "listOfDictOfMe": None
        }
    }
    assert model.dict_of_me == {"me": RecursiveModel({
        "name": "it's me!",
        "listOfMe": None,
        "dictOfMe": None,
        "dictOfListOfMe": None,
        "listOfDictOfMe": None
    })}

    assert model['dictOfListOfMe'] == {
        "many mes": [
            {
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None
            }
        ]
    }
    assert model.dict_of_list_of_me == {
        "many mes": [
            RecursiveModel({
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None
            })
        ]
    }
    assert model['listOfDictOfMe'] == [
        {"me": {
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None
            }
        }
    ]
    assert model.list_of_dict_of_me == [{
        "me": RecursiveModel({
            "name": "it's me!",
            "listOfMe": None,
            "dictOfMe": None,
            "dictOfListOfMe": None,
            "listOfDictOfMe": None
        })
    }]

    assert json.loads(json.dumps(model)) == model == dict_response
