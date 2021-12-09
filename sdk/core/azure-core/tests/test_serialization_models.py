# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import dataclasses
import json
import datetime
from typing import Any, List, Literal, Dict, Sequence, Set, Tuple, Optional
import pytest
import isodate
from azure.core.serialization import Model, rest_field

def modify_args(init):
    def _wrapper(self, **kwargs):
        init(self, **{
            self._get_property_name(kwarg) or kwarg: value
            for kwarg, value in kwargs.items()
        })
    return _wrapper

class BasicResource(Model):
    platform_update_domain_count: int = rest_field(name="platformUpdateDomainCount")  # How many times the platform update domain has been counted
    platform_fault_domain_count: int = rest_field(name="platformFaultDomainCount")  # How many times the platform fault domain has been counted
    virtual_machines: List[Any] = rest_field(name="virtualMachines")  # List of virtual machines

    def __init__(
        self,
        *,
        platform_update_domain_count: int,
        platform_fault_domain_count: int,
        virtual_machines: List[Any],
        **kwargs
    ):
        super().__init__(
            platform_update_domain_count=platform_update_domain_count,
            platform_fault_domain_count=platform_fault_domain_count,
            virtual_machines=virtual_machines,
            **kwargs
        )

class Pet(Model):

    name: str = rest_field()  # my name
    species: str = rest_field()  # my species

def test_model_and_dict_equal():

    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    model = BasicResource(platform_update_domain_count=5, platform_fault_domain_count=3, virtual_machines=[])
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
        dict_response['virtualMachines'])

def test_json_roundtrip():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    model = BasicResource(platform_update_domain_count=5, platform_fault_domain_count=3, virtual_machines=[])
    assert json.dumps(model) == '{"platformUpdateDomainCount": 5, "platformFaultDomainCount": 3, "virtualMachines": []}'
    assert json.loads(json.dumps(model)) == model == dict_response

def test_has_no_property():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": [],
        "noprop": "bonjour!"
    }
    model = BasicResource(
        platform_update_domain_count=5,
        platform_fault_domain_count=3,
        virtual_machines=[],
        noprop="bonjour!"
    )
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
        no_prop: str = rest_field(name="noprop")

    model = BasicResourceWithProperty(
        platform_update_domain_count=5,
        platform_fault_domain_count=3,
        virtual_machines=[],
        noprop="bonjour!"
    )
    assert (
        model.no_prop ==
        model["noprop"] ==
        dict_response["noprop"] ==
        "bonjour!"
    )

def test_original_and_attr_name_same():

    class MyModel(Model):
        hello: str = rest_field()

    dict_response = {"hello": "nihao"}
    model = MyModel(hello="nihao")
    assert model.hello == model["hello"] == dict_response["hello"]

class OptionalModel(Model):
    optional_str: Optional[str] = rest_field()
    optional_time: Optional[datetime.time] = rest_field()
    optional_dict: Optional[Dict[str, Optional[Pet]]] = rest_field(name="optionalDict")
    optional_model: Optional[Pet] = rest_field()
    optional_myself: Optional["OptionalModel"] = rest_field()

def test_optional_property():

    dict_response = {
        "optional_str": "hello!",
        "optional_time": None,
        "optionalDict": {
            "Eugene": {
                "name": "Eugene",
                "species": "Dog",
            },
            "Lady": None,
        },
        "optional_model": None,
        "optional_myself": {
            "optional_str": None,
            "optional_time": '11:34:56',
            "optionalDict": None,
            "optional_model": {
                "name": "Lady",
                "species": "Newt"
            },
            "optional_myself": None
        }
    }

    model = OptionalModel(**dict_response)
    assert model.optional_str == model["optional_str"] == "hello!"
    assert model.optional_time == model["optional_time"] == None
    assert model.optional_dict == model["optionalDict"] == {
        "Eugene": {
            "name": "Eugene",
            "species": "Dog",
        },
        "Lady": None,
    }
    assert model.optional_dict["Eugene"].name == model.optional_dict["Eugene"]["name"] == "Eugene"
    assert model.optional_dict["Lady"] is None

    assert model.optional_myself == model["optional_myself"] == {
        "optional_str": None,
        "optional_time": '11:34:56',
        "optionalDict": None,
        "optional_model": {
            "name": "Lady",
            "species": "Newt"
        },
        "optional_myself": None
    }
    assert model.optional_myself.optional_str is None
    assert model.optional_myself.optional_time == datetime.time(11, 34, 56)
    assert model.optional_myself.optional_dict is None
    assert model.optional_myself.optional_model.name == "Lady"
    assert model.optional_myself.optional_model.species == "Newt"
    assert model.optional_myself.optional_myself is None

def test_modify_dict():
    model = BasicResource(
        platform_update_domain_count=5,
        platform_fault_domain_count=3,
        virtual_machines=[]
    )

    # now let's modify the model as a dict
    model["platformUpdateDomainCount"] = 100
    assert model.platform_update_domain_count == model["platformUpdateDomainCount"] == 100

def test_modify_property():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    model = BasicResource(
        platform_update_domain_count=5,
        platform_fault_domain_count=3,
        virtual_machines=[]
    )

    # now let's modify the model through it's properties
    model.platform_fault_domain_count = 2000
    model['platformFaultDomainCount']
    assert model.platform_fault_domain_count == model["platformFaultDomainCount"] == 2000

def test_property_is_a_type():
    class Fish(Model):
        name: str = rest_field()
        species: Literal['Salmon', 'Halibut'] = rest_field()

    class Fishery(Model):
        fish: Fish = rest_field()

    fishery = Fishery(**{"fish": {"name": "Benjamin", "species": "Salmon"}})
    assert isinstance(fishery.fish, Fish)
    assert fishery.fish.name == fishery.fish['name'] == fishery['fish']['name'] == "Benjamin"
    assert fishery.fish.species == fishery.fish['species'] == fishery['fish']['species'] == "Salmon"

def test_datetime_deserialization():
    class DatetimeModel(Model):
        datetime_value: datetime.datetime = rest_field(name="datetimeValue")

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    model = DatetimeModel(**{"datetimeValue": val_str})
    assert model['datetimeValue'] == val_str
    assert model.datetime_value == val

    class BaseModel(Model):
        my_prop: DatetimeModel = rest_field(name="myProp")

    model = BaseModel(**{"myProp": {"datetimeValue": val_str}})
    assert isinstance(model.my_prop, DatetimeModel)
    assert model.my_prop['datetimeValue'] == model['myProp']['datetimeValue'] == val_str
    assert model.my_prop.datetime_value == val

def test_date_deserialization():
    class DateModel(Model):
        date_value: datetime.date = rest_field(name="dateValue")

    val_str = "2016-02-29"
    val = isodate.parse_date(val_str)
    model = DateModel(**{"dateValue": val_str})
    assert model['dateValue'] == val_str
    assert model.date_value == val

    class BaseModel(Model):
        my_prop: DateModel = rest_field(name="myProp")

    model = BaseModel(**{"myProp": {"dateValue": val_str}})
    assert isinstance(model.my_prop, DateModel)
    assert model.my_prop['dateValue'] == model['myProp']['dateValue'] == val_str
    assert model.my_prop.date_value == val

def test_time_deserialization():
    class TimeModel(Model):
        time_value: datetime.time = rest_field(name="timeValue")

    val_str = '11:34:56'
    val = datetime.time(11, 34, 56)
    model = TimeModel(**{"timeValue": val_str})
    assert model['timeValue'] == val_str
    assert model.time_value == val

    class BaseModel(Model):
        my_prop: TimeModel = rest_field(name="myProp")

    model = BaseModel(**{"myProp": {"timeValue": val_str}})
    assert isinstance(model.my_prop, TimeModel)
    assert model.my_prop['timeValue'] == model['myProp']['timeValue'] == val_str
    assert model.my_prop.time_value == val

class SimpleRecursiveModel(Model):
    name: str = rest_field()
    me: "SimpleRecursiveModel" = rest_field()

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

    model = SimpleRecursiveModel(**dict_response)
    assert model['name'] == model.name == "Snoopy"
    assert model['me'] == {
        "name": "Egg",
        "me": {
            "name": "Chicken"
        }
    }
    assert isinstance(model.me, SimpleRecursiveModel)
    assert model.me['name'] == model.me.name == "Egg"
    assert model.me['me'] == {"name": "Chicken"}
    assert model.me.me.name == "Chicken"

def test_dictionary_deserialization():
    class DictionaryModel(Model):
        prop: Dict[str, datetime.datetime] = rest_field()

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    dict_response = {
        "prop": {
            "datetime": val_str
        }
    }
    model = DictionaryModel(**dict_response)
    assert model['prop'] == {"datetime": val_str}
    assert model.prop == {"datetime": val}

def test_dictionary_deserialization_model():

    class DictionaryModel(Model):
        prop: Dict[str, Pet] = rest_field()

    dict_response = {
        "prop": {
            "Eugene": {
                "name": "Eugene",
                "species": "Dog",
            },
            "Lady": {
                "name": "Lady",
                "species": "Newt",
            }
        }
    }

    model = DictionaryModel(**dict_response)
    assert model['prop'] == {
        "Eugene": {
            "name": "Eugene",
            "species": "Dog",
        },
        "Lady": {
            "name": "Lady",
            "species": "Newt",
        }
    }
    assert model.prop == {
        "Eugene": Pet(**{"name": "Eugene", "species": "Dog"}),
        "Lady": Pet(**{"name": "Lady", "species": "Newt"})
    }
    assert model.prop["Eugene"].name == model.prop["Eugene"]["name"] == "Eugene"
    assert model.prop["Eugene"].species == model.prop["Eugene"]["species"] == "Dog"
    assert model.prop["Lady"].name == model.prop["Lady"]["name"] == "Lady"
    assert model.prop["Lady"].species == model.prop["Lady"]["species"] == "Newt"

def test_list_deserialization():
    class ListModel(Model):
        prop: List[datetime.datetime] = rest_field()

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    dict_response = {
        "prop": [val_str, val_str]
    }
    model = ListModel(**dict_response)
    assert model['prop'] == [val_str, val_str]
    assert model.prop == [val, val]

def test_list_deserialization_model():
    class ListModel(Model):
        prop: List[Pet] = rest_field()

    dict_response = {
        "prop": [
            {"name": "Eugene", "species": "Dog"},
            {"name": "Lady", "species": "Newt"}
        ]
    }
    model = ListModel(**dict_response)
    assert model["prop"] == [
        {"name": "Eugene", "species": "Dog"},
        {"name": "Lady", "species": "Newt"}
    ]
    assert model.prop == [
        Pet(**{"name": "Eugene", "species": "Dog"}),
        Pet(**{"name": "Lady", "species": "Newt"})
    ]
    assert len(model.prop) == 2
    assert model.prop[0].name == model.prop[0]["name"] == "Eugene"
    assert model.prop[0].species == model.prop[0]["species"] == "Dog"
    assert model.prop[1].name == model.prop[1]["name"] == "Lady"
    assert model.prop[1].species == model.prop[1]["species"] == "Newt"

def test_set_deserialization():
    class SetModel(Model):
        prop: Set[datetime.datetime] = rest_field()

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    dict_response = {
        "prop": set([val_str, val_str])
    }
    model = SetModel(**dict_response)
    assert model['prop'] == set([val_str, val_str])
    assert model.prop == set([val, val])

def test_tuple_deserialization():
    class TupleModel(Model):
        prop: Tuple[str, datetime.datetime] = rest_field()

    val_str = "9999-12-31T23:59:59.999Z"
    val = isodate.parse_datetime(val_str)
    dict_response = {
        "prop": (val_str, val_str)
    }
    model = TupleModel(**dict_response)
    assert model['prop'] == (val_str, val_str)
    assert model.prop == (val_str, val)

def test_list_of_tuple_deserialization_model():

    class Owner(Model):
        name: str = rest_field()
        pet: Pet = rest_field()

    class ListOfTupleModel(Model):
        prop: List[Tuple[Pet, Owner]] = rest_field()

    eugene = {"name": "Eugene", "species": "Dog"}
    lady = {"name": "Lady", "species": "Newt"}
    giacamo = {"name": "Giacamo", "pet": eugene}
    elizabeth = {"name": "Elizabeth", "pet": lady}

    dict_response = {
        "prop": [(eugene, giacamo), (lady, elizabeth)]
    }
    model = ListOfTupleModel(**dict_response)
    assert (
        model['prop'] ==
        model.prop ==
        [(eugene, giacamo), (lady, elizabeth)] ==
        [(Pet(**eugene), Owner(**giacamo)), (Pet(**lady), Owner(**elizabeth))]
    )
    assert len(model.prop[0]) == len(model['prop'][0]) == 2
    assert model.prop[0][0].name == model.prop[0][0]['name'] == "Eugene"
    assert model.prop[0][0].species == model.prop[0][0]['species'] == "Dog"
    assert model.prop[0][1].name == "Giacamo"
    assert model.prop[0][1].pet == model.prop[0][0]
    assert model.prop[0][1].pet.name == model.prop[0][1]["pet"]["name"] == "Eugene"
    assert model.prop[1][0] == model.prop[1][1].pet

class RecursiveModel(Model):
    name: str = rest_field()
    list_of_me: Optional[List["RecursiveModel"]] = rest_field(name="listOfMe")
    dict_of_me: Optional[Dict[str, "RecursiveModel"]] = rest_field(name="dictOfMe")
    dict_of_list_of_me: Optional[Dict[str, List["RecursiveModel"]]] = rest_field(name="dictOfListOfMe")
    list_of_dict_of_me: Optional[List[Dict[str, "RecursiveModel"]]] = rest_field(name="listOfDictOfMe")

def test_model_recursion_complex():

    dict_response = {
        "name": "it's me!",
        "listOfMe": [
            {
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None,
            }
        ],
        "dictOfMe": {
            "me": {
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None,
            }
        },
        "dictOfListOfMe": {
            "many mes": [
                {
                    "name": "it's me!",
                    "listOfMe": None,
                    "dictOfMe": None,
                    "dictOfListOfMe": None,
                    "listOfDictOfMe": None,
                }
            ]
        },
        "listOfDictOfMe": [
            {"me": {
                    "name": "it's me!",
                    "listOfMe": None,
                    "dictOfMe": None,
                    "dictOfListOfMe": None,
                    "listOfDictOfMe": None,
                }
            }
        ]
    }

    model = RecursiveModel(**dict_response)
    assert model.name == model['name'] == "it's me!"
    assert model['listOfMe'] == [
        {
            "name": "it's me!",
            "listOfMe": None,
            "dictOfMe": None,
            "dictOfListOfMe": None,
            "listOfDictOfMe": None,
        }
    ]
    assert model.list_of_me == [RecursiveModel(**{
        "name": "it's me!",
        "listOfMe": None,
        "dictOfMe": None,
        "dictOfListOfMe": None,
        "listOfDictOfMe": None,
    })]
    assert model.list_of_me[0].name == "it's me!"
    assert model.list_of_me[0].list_of_me is None
    assert isinstance(model.list_of_me, List)
    assert isinstance(model.list_of_me[0], RecursiveModel)

    assert model['dictOfMe'] == {
        "me": {
            "name": "it's me!",
            "listOfMe": None,
            "dictOfMe": None,
            "dictOfListOfMe": None,
            "listOfDictOfMe": None,
        }
    }
    assert model.dict_of_me == {"me": RecursiveModel(**{
        "name": "it's me!",
        "listOfMe": None,
        "dictOfMe": None,
        "dictOfListOfMe": None,
        "listOfDictOfMe": None,
    })}

    assert isinstance(model.dict_of_me, Dict)
    assert isinstance(model.dict_of_me["me"], RecursiveModel)

    assert model['dictOfListOfMe'] == {
        "many mes": [
            {
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None,
            }
        ]
    }
    assert model.dict_of_list_of_me == {
        "many mes": [
            RecursiveModel(**{
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None,
            })
        ]
    }
    assert isinstance(model.dict_of_list_of_me, Dict)
    assert isinstance(model.dict_of_list_of_me["many mes"], List)
    assert isinstance(model.dict_of_list_of_me["many mes"][0], RecursiveModel)

    assert model['listOfDictOfMe'] == [
        {"me": {
                "name": "it's me!",
                "listOfMe": None,
                "dictOfMe": None,
                "dictOfListOfMe": None,
                "listOfDictOfMe": None,
            }
        }
    ]
    assert model.list_of_dict_of_me == [{
        "me": RecursiveModel(**{
            "name": "it's me!",
            "listOfMe": None,
            "dictOfMe": None,
            "dictOfListOfMe": None,
            "listOfDictOfMe": None,
        })
    }]
    assert isinstance(model.list_of_dict_of_me, List)
    assert isinstance(model.list_of_dict_of_me[0], Dict)
    assert isinstance(model.list_of_dict_of_me[0]["me"], RecursiveModel)

    assert json.loads(json.dumps(model)) == model == dict_response

def test_literals():

    class LiteralModel(Model):
        species: Literal["Mongose", "Eagle", "Penguin"] = rest_field()
        age: Literal[1, 2, 3] = rest_field()

    dict_response = {
        "species": "Mongoose",
        "age": 3
    }
    model = LiteralModel(**dict_response)
    assert model.species == model["species"] == "Mongoose"
    assert model.age == model["age"] == 3

    dict_response = {
        "species": "invalid",
        "age": 5
    }
    model = LiteralModel(**dict_response)
    assert model["species"] == "invalid"
    assert model["age"] == 5

    assert model.species == "invalid"

    assert model.age == 5

def test_deserialization_callback_override():

    def _callback(obj):
        return [str(entry) for entry in obj]

    class MyModel(Model):
        prop: Sequence[int] = rest_field()

    model_without_callback = MyModel(prop=[1.3, 2.4, 3.5])
    assert model_without_callback.prop == [1, 2, 3]
    assert model_without_callback['prop'] == [1.3, 2.4, 3.5]

    class MyModel(Model):
        prop: Any = rest_field(type=_callback)

    model_with_callback = MyModel(prop=[1.3, 2.4, 3.5])
    assert model_with_callback.prop == ["1.3", "2.4", "3.5"]
    assert model_with_callback['prop'] == model_without_callback['prop']

def test_deserialization_callback_override_parent():

    class ParentNoCallback(Model):
        prop: Sequence[float] = rest_field()

    def _callback(obj):
        return set([str(entry) for entry in obj])

    class ChildWithCallback(ParentNoCallback):
        prop: Sequence[float] = rest_field(type=_callback)

    parent_model = ParentNoCallback(prop=[1, 1, 2, 3])
    assert parent_model.prop == parent_model["prop"] == [1, 1, 2, 3]

    child_model = ChildWithCallback(prop=[1, 1, 2, 3])
    assert child_model.prop == set(["1", "1", "2", "3"])
    assert child_model['prop'] == [1, 1, 2, 3]
