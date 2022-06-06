# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import datetime
from typing import Any, List, Literal, Dict, Sequence, Set, Tuple, Optional, Union
import pytest
import isodate
from azure.core.serialization import Model, rest_field, rest_discriminator

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
    assert model.optional_dict
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
    assert model.optional_myself
    assert model.optional_myself.optional_str is None
    assert model.optional_myself.optional_time == datetime.time(11, 34, 56)
    assert model.optional_myself.optional_dict is None
    assert model.optional_myself.optional_model
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
    assert model.list_of_me
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

def test_inheritance_basic():
    def _callback(obj):
        return [str(e) for e in obj]

    class Parent(Model):
        parent_prop: List[int] = rest_field(name="parentProp", type=_callback)
        prop: str = rest_field()

    class Child(Parent):
        pass

    c = Child(parent_prop=[1, 2, 3], prop="hello")
    assert c == {"parentProp": [1, 2, 3], "prop": "hello"}
    assert c.parent_prop == ["1", "2", "3"]
    assert c.prop == "hello"


class A(Model):
    prop: int = rest_field()

    def __init__(self, *, prop: Any, **kwargs):
        super().__init__(prop=prop, **kwargs)

class B(A):
    prop: str = rest_field()
    bcd_prop: Optional[List["B"]] = rest_field(name="bcdProp")

    def __init__(self, *, prop: Any, bcd_prop: Optional[List["B"]] = None, **kwargs):
        super().__init__(prop=prop, bcd_prop=bcd_prop, **kwargs)

class C(B):
    prop: float = rest_field()
    cd_prop: A = rest_field(name="cdProp")

    def __init__(
        self,
        *,
        prop: Any,
        bcd_prop: List[B],
        cd_prop: A,
        **kwargs
    ):
        super().__init__(
            prop=prop,
            bcd_prop=bcd_prop,
            cd_prop=cd_prop,
            **kwargs
        )

class D(C):
    d_prop: Tuple[A, B, C, Optional["D"]] = rest_field(name="dProp")

    def __init__(
        self,
        *,
        prop: Any,
        bcd_prop: List[B],
        cd_prop: A,
        d_prop: Tuple[A, B, C, Optional["D"]],
        **kwargs
    ):
        super().__init__(
            prop=prop,
            bcd_prop=bcd_prop,
            cd_prop=cd_prop,
            d_prop=d_prop,
            **kwargs
        )

def test_inheritance_4_levels():
    a = A(prop=3.4)
    assert a.prop == 3
    assert a['prop'] == 3.4
    assert a == {"prop": 3.4}
    assert isinstance(a, Model)

    b = B(prop=3.4, bcd_prop=[B(prop=4.3)])
    assert b.prop == "3.4"
    assert b['prop'] == 3.4
    assert b.bcd_prop == [B(prop=4.3)]
    assert b.bcd_prop
    assert b.bcd_prop[0].prop == "4.3"
    assert b.bcd_prop[0].bcd_prop is None
    assert b == {"prop": 3.4, "bcdProp": [{"prop": 4.3, "bcdProp": None}]}
    assert isinstance(b, B)
    assert isinstance(b, A)

    c = C(prop=3.4, bcd_prop=[b], cd_prop=a)
    assert c.prop == c['prop'] == 3.4
    assert c.bcd_prop == [b]
    assert c.bcd_prop
    assert isinstance(c.bcd_prop[0], B)
    assert c['bcdProp'] == [b] == [{"prop": 3.4, "bcdProp": [{"prop": 4.3, "bcdProp": None}]}]
    assert c.cd_prop == a
    assert c['cdProp'] == a == {"prop": 3.4}
    assert isinstance(c.cd_prop, A)

    d = D(prop=3.4, bcd_prop=[b], cd_prop=a, d_prop=(a, b, c, D(prop=3.4, bcd_prop=[b], cd_prop=a, d_prop=(a, b, c, None))))
    assert d == {
        'prop': 3.4,
        'bcdProp': [b],
        'cdProp': a,
        'dProp': (
            a, b, c,
            {
                'prop': 3.4,
                'bcdProp': [b],
                'cdProp': a,
                'dProp': (
                    a, b, c, None
                )
            }
        )
    }
    assert d.prop == d['prop'] == 3.4
    assert d.bcd_prop == [b]
    assert d.bcd_prop
    assert isinstance(d.bcd_prop[0], B)
    assert d.cd_prop == a
    assert isinstance(d.cd_prop, A)
    assert d.d_prop[0] == a # at a
    assert isinstance(d.d_prop[0], A)
    assert d.d_prop[1] == b
    assert isinstance(d.d_prop[1], B)
    assert d.d_prop[2] == c
    assert isinstance(d.d_prop[2], C)
    assert isinstance(d.d_prop[3], D)

    assert isinstance(d.d_prop[3].d_prop[0], A)
    assert isinstance(d.d_prop[3].d_prop[1], B)
    assert isinstance(d.d_prop[3].d_prop[2], C)
    assert d.d_prop[3].d_prop[3] is None

def test_multiple_inheritance_basic():
    class ParentOne(Model):
        parent_one_prop: str = rest_field(name="parentOneProp")

        def __init__(
            self,
            *,
            parent_one_prop: str,
            **kwargs
        ):
            super().__init__(parent_one_prop=parent_one_prop, **kwargs)

    class ParentTwo(Model):
        parent_two_prop: int = rest_field(name="parentTwoProp", type=lambda x: str(x))

        def __init__(
            self,
            *,
            parent_two_prop: int,
            **kwargs
        ):
            super().__init__(parent_two_prop=parent_two_prop, **kwargs)

    class Child(ParentOne, ParentTwo):

        def __init__(
            self,
            *,
            parent_one_prop: str,
            parent_two_prop: int,
            **kwargs
        ):
            super().__init__(parent_one_prop=parent_one_prop, parent_two_prop=parent_two_prop, **kwargs)

    c = Child(parent_one_prop="Hello", parent_two_prop=3)
    assert c == {"parentOneProp": "Hello", "parentTwoProp": 3}
    assert c.parent_one_prop == "Hello"
    assert c.parent_two_prop == "3"
    assert isinstance(c, Child)
    assert isinstance(c, ParentOne)
    assert isinstance(c, ParentTwo)

def test_multiple_inheritance_mro():
    class A(Model):
        prop: str = rest_field()

        def __init__(self, *, prop: str) -> None:
            super().__init__(prop=prop)

    class B(Model):
        prop: int = rest_field()

        def __init__(self, *, prop: str) -> None:
            super().__init__(prop=prop)

    class C(A, B):
        pass

    assert A(prop="1").prop == "1"
    assert B(prop="1").prop == 1
    assert C(prop="1").prop == "1"  # A should take precedence over B

class Feline(Model):
    meows: bool = rest_field()
    hisses: bool = rest_field()
    siblings: Optional[List["Feline"]] = rest_field()

    def __init__(
        self,
        *,
        meows: bool,
        hisses: bool,
        siblings: Optional[List["Feline"]] = None,
        **kwargs
    ):
        super().__init__(
            meows=meows,
            hisses=hisses,
            siblings=siblings,
            **kwargs
        )

class Owner(Model):
    first_name: str = rest_field(name="firstName", type=lambda x: x.capitalize())
    last_name: str = rest_field(name="lastName", type=lambda x: x.capitalize())

    def __init__(
        self,
        *,
        first_name: str,
        last_name: str,
        **kwargs
    ):
        super().__init__(
            first_name=first_name, last_name=last_name, **kwargs
        )

class PetModel(Model):
    name: str = rest_field()
    owner: Owner = rest_field()

    def __init__(self, *, name: str, owner: Owner, **kwargs):
        super().__init__(name=name, owner=owner, **kwargs)

class Cat(PetModel, Feline):
    likes_milk: bool = rest_field(name="likesMilk", type=lambda x: True)

    def __init__(
        self,
        *,
        name: str,
        owner: Owner,
        meows: bool,
        hisses: bool,
        likes_milk: bool,
        siblings: Optional[List[Feline]],
        **kwargs
    ):
        super().__init__(
            name=name,
            owner=owner,
            meows=meows,
            hisses=hisses,
            likes_milk=likes_milk,
            siblings=siblings,
            **kwargs
        )

class CuteThing(Model):
    how_cute_am_i: float = rest_field(name="howCuteAmI")

    def __init__(self, *, how_cute_am_i: float, **kwargs):
        super().__init__(how_cute_am_i=how_cute_am_i, **kwargs)

class Kitten(Cat, CuteThing):
    eats_mice_yet: bool = rest_field(name="eatsMiceYet")

    def __init__(
        self,
        *,
        name: str,
        owner: Owner,
        meows: bool,
        hisses: bool,
        likes_milk: bool,
        siblings: Optional[List[Feline]],
        how_cute_am_i: float,
        eats_mice_yet: bool,
        **kwargs
    ):
        super().__init__(
            name=name,
            owner=owner,
            meows=meows,
            hisses=hisses,
            likes_milk=likes_milk,
            siblings=siblings,
            how_cute_am_i=how_cute_am_i,
            eats_mice_yet=eats_mice_yet,
            **kwargs
        )


def test_multiple_inheritance_complex():
    cat = Cat(
        name="Stephanie",
        owner=Owner(first_name="cecil", last_name="cai"),  # gets capitalized in attr
        meows=True,
        hisses=True,
        likes_milk=False,  # likes_milk will change to True on the attribute
        siblings=[Feline(meows=True, hisses=False)]
    )
    assert cat == {
        "name": "Stephanie",
        "owner": {
            "firstName": "cecil",
            "lastName": "cai",
        },
        "meows": True,
        "hisses": True,
        "likesMilk": False,
        "siblings": [{
            "meows": True,
            "hisses": False,
            "siblings": None
        }]
    }
    assert cat.name == "Stephanie"
    assert isinstance(cat.owner, Owner)
    assert cat.owner.first_name == "Cecil"
    assert cat.owner.last_name == "Cai"
    assert cat.meows
    assert cat.hisses
    assert cat.likes_milk
    assert cat.siblings
    assert len(cat.siblings) == 1
    assert isinstance(cat.siblings[0], Feline)

    kitten = Kitten(
        name="Stephanie",
        owner=Owner(first_name="cecil", last_name="cai"),  # gets capitalized in attr
        meows=True,
        hisses=True,
        likes_milk=False,  # likes_milk will change to True on the attribute
        siblings=[Feline(meows=True, hisses=False)],
        how_cute_am_i=1.0,
        eats_mice_yet=True,
    )
    assert kitten == {
        "name": "Stephanie",
        "owner": {
            "firstName": "cecil",
            "lastName": "cai",
        },
        "meows": True,
        "hisses": True,
        "likesMilk": False,
        "siblings": [{
            "meows": True,
            "hisses": False,
            "siblings": None
        }],
        "howCuteAmI": 1.0,
        "eatsMiceYet": True,
    }
    assert kitten.name == "Stephanie"
    assert isinstance(kitten.owner, Owner)
    assert kitten.owner.first_name == "Cecil"
    assert kitten.owner.last_name == "Cai"
    assert kitten.meows
    assert kitten.hisses
    assert kitten.likes_milk
    assert kitten.siblings
    assert len(kitten.siblings) == 1
    assert isinstance(kitten.siblings[0], Feline)
    assert kitten.eats_mice_yet
    assert kitten.how_cute_am_i == 1.0
    assert isinstance(kitten, PetModel)
    assert isinstance(kitten, Cat)
    assert isinstance(kitten, Feline)
    assert isinstance(kitten, CuteThing)

class Animal(Model):

    kind: str = rest_discriminator()
    is_domesticated: str = rest_field(name="isDomesticated")

    def __init__(self, *, genus: str, **kwargs):
        super().__init__(genus=genus, **kwargs)

class Fish(Animal, discriminator="fish"):
    fish_type: str = rest_field(name="fishType")
    siblings: List["Fish"] = rest_field()

    def __init__(self, *, genus: str, fish_type: str, siblings: List["Fish"], **kwargs):
        super().__init__(genus=genus, **kwargs)
        self.fish_type = fish_type
        self.siblings = siblings
        self.kind: Literal["fish"] = "fish"


class Salmon(Fish, discriminator="salmon"):
    is_sashimi: bool = rest_field(name="isSashimi")

    def __init__(self, *, genus: str, fish_type: str, siblings: List["Fish"], is_sashimi: bool, **kwargs):
        super().__init__(
            genus=genus,
            fish_type=fish_type,
            siblings=siblings,
            **kwargs
        )
        self.is_sashimi = is_sashimi
        self.kind: Literal["salmon"] = "salmon"

class Cat(Animal, discriminator="cat"):
    has_kitten: bool = rest_field(name="hasKitten")

    def __init__(self, *, genus: str, has_kitten: bool, **kwargs):
        super().__init__(genus=genus, **kwargs)
        self.has_kitten = has_kitten
        self.kind: Literal["cat"] = "cat"

class Dog(Animal, discriminator="dog"):
    has_puppy: bool = rest_field(name="hasPuppy")
    enemies: List[Cat] = rest_field()

    def __init__(self, *, genus: str, has_puppy: bool, enemies: List[Cat], **kwargs):
        super().__init__(genus=genus, **kwargs)
        self.has_puppy = has_puppy
        self.enemies = enemies
        self.kind: Literal["dog"] = "dog"

def test_polymorphism():
    animal = Animal(genus="idk", kind="cat")
    cat = Cat(genus="idk", has_kitten=True)

# def get_animal(raw_response: Dict[str, Any]) -> Union[Fish, Cat, Dog]:
#     if raw_response["kind"] == "Cat":
#         return Cat(**raw_response)
#     if raw_response["kind"] == "fish":
#         return Fish(**raw_response)
#     if raw_response["kind"] == "Dog":
#         return Dog(**raw_response)
#     return Animal(**raw_response)  # type: ignore

# animal = get_animal({"kind": "Cat", "hasKitten": False})
# if animal.kind == "cat":
#     print(animal.has_kitten)
# elif animal.kind == "dog":
#     print(animal.enemies)
