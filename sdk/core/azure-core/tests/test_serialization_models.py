# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import datetime
from typing import Any, List, Literal
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

        @rest_property(name="name")
        def name(self) -> str:
            """My Fish name"""

        @rest_property(name="species")
        def species(self) -> Literal['Salmon', 'Halibut']:
            """My species"""

    class Fishery(Model):

        @rest_property(name="fish")
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
