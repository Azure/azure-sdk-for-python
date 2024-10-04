# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from unittest.mock import patch

import pytest
from azure.core.utils import case_insensitive_dict
from azure.core.utils._utils import get_running_async_lock
from azure.core.pipeline.policies._utils import parse_retry_after, get_challenge_parameter


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
    dict_response = {"platformUpdateDomainCount": 5, "platformFaultDomainCount": 3, "virtualMachines": []}
    a = case_insensitive_dict(platformUpdateDomainCount=5, platformFaultDomainCount=3, virtualMachines=[])
    b = case_insensitive_dict(
        zip(["platformUpdateDomainCount", "platformFaultDomainCount", "virtualMachines"], [5, 3, []])
    )
    c = case_insensitive_dict(
        [("platformFaultDomainCount", 3), ("platformUpdateDomainCount", 5), ("virtualMachines", [])]
    )
    d = case_insensitive_dict({"virtualMachines": [], "platformFaultDomainCount": 3, "platformUpdateDomainCount": 5})
    e = case_insensitive_dict({"platformFaultDomainCount": 3, "virtualMachines": []}, platformUpdateDomainCount=5)
    f = case_insensitive_dict(dict_response)
    g = case_insensitive_dict(**dict_response)
    assert a == b == c == d == e == f == g
    dicts = [a, b, c, d, e, f, g]
    for d in dicts:
        assert len(d) == 3
        assert d["platformUpdateDomainCount"] == d["platformupdatedomaincount"] == d["PLATFORMUPDATEDOMAINCOUNT"] == 5
        assert d["platformFaultDomainCount"] == d["platformfaultdomaincount"] == d["PLATFORMFAULTDOMAINCOUNT"] == 3
        assert d["virtualMachines"] == d["virtualmachines"] == d["VIRTUALMACHINES"] == []


def test_case_insensitive_dict_cant_compare():
    my_dict = case_insensitive_dict({"accept": "application/json"})
    assert my_dict != "accept"


def test_case_insensitive_dict_lowerkey_items():
    my_dict = case_insensitive_dict({"accept": "application/json"})
    assert list(my_dict.lowerkey_items()) == [("accept", "application/json")]


@pytest.mark.parametrize(
    "other, expected",
    (
        ({"PLATFORMUPDATEDOMAINCOUNT": 5}, True),
        ({}, False),
        (None, False),
    ),
)
def test_case_insensitive_dict_equality(other, expected):
    my_dict = case_insensitive_dict({"platformUpdateDomainCount": 5})
    result = my_dict == other
    assert result == expected


def test_case_insensitive_dict_keys():
    keys = ["One", "TWO", "tHrEe", "four"]
    my_dict = case_insensitive_dict({key: idx for idx, key in enumerate(keys, 1)})
    dict_keys = list(my_dict.keys())

    assert dict_keys == keys


def test_case_insensitive_copy():
    keys = ["One", "TWO", "tHrEe", "four"]
    my_dict = case_insensitive_dict({key: idx for idx, key in enumerate(keys, 1)})
    copy_my_dict = my_dict.copy()
    assert copy_my_dict is not my_dict
    assert copy_my_dict == my_dict


def test_case_insensitive_keys_present(accept_cases):
    my_dict = case_insensitive_dict({"accept": "application/json"})

    for key in accept_cases:
        assert key in my_dict


def test_case_insensitive_keys_delete(accept_cases):
    my_dict = case_insensitive_dict({"accept": "application/json"})

    for key in accept_cases:
        del my_dict[key]
        assert key not in my_dict
        my_dict[key] = "application/json"


def test_case_iter():
    keys = ["One", "TWO", "tHrEe", "four"]
    my_dict = case_insensitive_dict({key: idx for idx, key in enumerate(keys, 1)})

    for key in my_dict:
        assert key in keys


@pytest.mark.asyncio
async def test_get_running_async_module_asyncio():
    import asyncio

    assert isinstance(get_running_async_lock(), asyncio.Lock)


@pytest.mark.trio
async def test_get_running_async_module_trio():
    import trio

    assert isinstance(get_running_async_lock(), trio.Lock)


def test_get_running_async_module_sync():
    with patch.dict("sys.modules"):
        # Ensure trio isn't in sys.modules (i.e. imported).
        sys.modules.pop("trio", None)
        with pytest.raises(RuntimeError):
            get_running_async_lock()


def test_parse_retry_after():
    ret = parse_retry_after("100")
    assert ret == 100
    ret = parse_retry_after("Fri, 1 Oct 2100 00:00:00 GMT")
    assert ret > 0
    ret = parse_retry_after("0")
    assert ret == 0
    ret = parse_retry_after("0.9")
    assert ret == 0.9


def test_get_challenge_parameter():
    headers = {
        "WWW-Authenticate": 'Bearer authorization_uri="https://login.microsoftonline.com/tenant-id", resource="https://vault.azure.net"'
    }
    assert (
        get_challenge_parameter(headers, "Bearer", "authorization_uri") == "https://login.microsoftonline.com/tenant-id"
    )
    assert get_challenge_parameter(headers, "Bearer", "resource") == "https://vault.azure.net"
    assert get_challenge_parameter(headers, "Bearer", "foo") is None

    headers = {
        "WWW-Authenticate": 'Bearer realm="", authorization_uri="https://login.microsoftonline.com/common/oauth2/authorize", error="insufficient_claims", claims="eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwidmFsdWUiOiIxNzI2MDc3NTk1In0sInhtc19jYWVlcnJvciI6eyJ2YWx1ZSI6IjEwMDEyIn19fQ=="'
    }
    assert (
        get_challenge_parameter(headers, "Bearer", "authorization_uri")
        == "https://login.microsoftonline.com/common/oauth2/authorize"
    )
    assert get_challenge_parameter(headers, "Bearer", "error") == "insufficient_claims"
    assert (
        get_challenge_parameter(headers, "Bearer", "claims")
        == "eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwidmFsdWUiOiIxNzI2MDc3NTk1In0sInhtc19jYWVlcnJvciI6eyJ2YWx1ZSI6IjEwMDEyIn19fQ=="
    )


def test_get_challenge_parameter_not_found():
    headers = {
        "WWW-Authenticate": 'Pop authorization_uri="https://login.microsoftonline.com/tenant-id", resource="https://vault.azure.net"'
    }
    assert get_challenge_parameter(headers, "Bearer", "resource") is None


def test_get_multi_challenge_parameter():
    headers = {
        "WWW-Authenticate": 'Bearer authorization_uri="https://login.microsoftonline.com/tenant-id", resource="https://vault.azure.net" Bearer authorization_uri="https://login.microsoftonline.com/tenant-id", resource="https://vault.azure.net"'
    }
    assert (
        get_challenge_parameter(headers, "Bearer", "authorization_uri") == "https://login.microsoftonline.com/tenant-id"
    )
    assert get_challenge_parameter(headers, "Bearer", "resource") == "https://vault.azure.net"
    assert get_challenge_parameter(headers, "Bearer", "foo") is None

    headers = {
        "WWW-Authenticate": 'Digest realm="foo@test.com", qop="auth,auth-int", nonce="123456abcdefg", opaque="123456", Bearer realm="", authorization_uri="https://login.microsoftonline.com/common/oauth2/authorize", error="insufficient_claims", claims="eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwidmFsdWUiOiIxNzI2MDc3NTk1In0sInhtc19jYWVlcnJvciI6eyJ2YWx1ZSI6IjEwMDEyIn19fQ=="'
    }
    assert (
        get_challenge_parameter(headers, "Bearer", "authorization_uri")
        == "https://login.microsoftonline.com/common/oauth2/authorize"
    )
    assert get_challenge_parameter(headers, "Bearer", "error") == "insufficient_claims"
    assert (
        get_challenge_parameter(headers, "Bearer", "claims")
        == "eyJhY2Nlc3NfdG9rZW4iOnsibmJmIjp7ImVzc2VudGlhbCI6dHJ1ZSwidmFsdWUiOiIxNzI2MDc3NTk1In0sInhtc19jYWVlcnJvciI6eyJ2YWx1ZSI6IjEwMDEyIn19fQ=="
    )
