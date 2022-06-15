# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.core.utils import case_insensitive_dict

@pytest.fixture()
def accept_cases():
    return ["accept", "Accept", "ACCEPT", "aCCePT"]

def test_case_insensitive_dict_basic(accept_cases):
    my_dict = case_insensitive_dict({"accept": "application/json"})
    for accept_case in accept_cases:
        assert my_dict[accept_case] == "application/json"

def test_case_insensitive_dict_override(accept_cases):
    for accept_case in accept_cases:
        my_dict = case_insensitive_dict({accept_case: "should-not/be-me"})
        my_dict["accept"] = "application/json"
        assert my_dict[accept_case] == my_dict["accept"] == "application/json"

def test_case_insensitive_dict_initialization():
    dict_response = {
        "platformUpdateDomainCount": 5,
        "platformFaultDomainCount": 3,
        "virtualMachines": []
    }
    a = case_insensitive_dict(platformUpdateDomainCount=5, platformFaultDomainCount=3, virtualMachines=[])
    b = case_insensitive_dict(zip(['platformUpdateDomainCount', 'platformFaultDomainCount', 'virtualMachines'], [5, 3, []]))
    c = case_insensitive_dict([('platformFaultDomainCount', 3), ('platformUpdateDomainCount', 5), ('virtualMachines', [])])
    d = case_insensitive_dict({'virtualMachines': [], 'platformFaultDomainCount': 3, 'platformUpdateDomainCount': 5})
    e = case_insensitive_dict({'platformFaultDomainCount': 3, 'virtualMachines': []}, platformUpdateDomainCount=5)
    f = case_insensitive_dict(dict_response)
    g = case_insensitive_dict(**dict_response)
    assert a == b == c == d == e == f == g
    dicts = [a, b, c, d, e, f, g]
    for d in dicts:
        assert len(d) == 3
        assert d['platformUpdateDomainCount'] == d['platformupdatedomaincount'] == d['PLATFORMUPDATEDOMAINCOUNT'] == 5
        assert d['platformFaultDomainCount'] == d['platformfaultdomaincount'] == d['PLATFORMFAULTDOMAINCOUNT'] == 3
        assert d['virtualMachines'] == d['virtualmachines'] == d['VIRTUALMACHINES'] == []

def test_case_insensitive_dict_cant_compare():
    my_dict = case_insensitive_dict({"accept": "application/json"})
    assert my_dict != "accept"

def test_case_insensitive_dict_lowerkey_items():
    my_dict = case_insensitive_dict({"accept": "application/json"})
    assert list(my_dict.lowerkey_items()) == [("accept","application/json")]

@pytest.mark.parametrize("other, expected", (
    ({"PLATFORMUPDATEDOMAINCOUNT": 5}, True),
    ({}, False),
    (None, False),
))
def test_case_insensitive_dict_equality(other, expected):
    my_dict = case_insensitive_dict({"platformUpdateDomainCount": 5})
    result = my_dict == other
    assert result == expected
