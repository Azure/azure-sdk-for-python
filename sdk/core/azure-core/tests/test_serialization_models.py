# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import List
import pytest
from azure.core.serialization import Model

def modify_args(init):
    def _wrapper(self, **kwargs):
        init(self, **{
            self._get_property_name(kwarg) or kwarg: value
            for kwarg, value in kwargs.items()
        })
    return _wrapper


class BasicResource(Model):
    _attribute_map = {
        "platform_update_domain_count": {"type": "platformUpdateDomainCount"},
        "platform_fault_domain_count": {"type": "platformFaultDomainCount"},
        "virtual_machines": {"type": "virtualMachines"}
    }

    @modify_args
    def __init__(
        self,
        *,
        platform_update_domain_count: int,
        platform_fault_domain_count: int,
        virtual_machines: List[str],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.platform_update_domain_count = platform_update_domain_count
        self.platform_fault_domain_count = platform_fault_domain_count
        self.virtual_machines = virtual_machines

def test_model_and_dict_equal():

    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    model = BasicResource(**dict_response)
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

    # check json.dumps, json.loads, check roundtrip is correct

def test_has_no_property():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": [],
        "noprop": "bonjour!"
    }
    model = BasicResource(**dict_response)
    assert (
        model.platform_update_domain_count ==
        model["platformUpdateDomainCount"] ==
        dict_response["platformUpdateDomainCount"] ==
        5
    )
    with pytest.raises(AttributeError) as ex:
        model.noprop

    assert str(ex.value) == "BasicResource instance has no attribute 'noprop'"
    assert model["noprop"] == dict_response["noprop"] == "bonjour!"

    # if we update attribute map, it should automatically work
    model._property_to_dict_name.append(("noprop", "noprop"))
    assert (
        model.noprop ==
        model["noprop"] ==
        dict_response["noprop"] ==
        "bonjour!"
    )

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
    assert model.platform_fault_domain_count == model["platformFaultDomainCount"] == 2000

# def test_
