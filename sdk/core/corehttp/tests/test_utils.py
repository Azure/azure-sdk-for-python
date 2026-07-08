# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from unittest.mock import patch

import pytest
from corehttp.utils import case_insensitive_dict
from corehttp.utils._utils import get_running_async_lock, CaseInsensitiveSet
from corehttp.runtime.policies._utils import parse_retry_after, sanitize_url


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


def test_get_running_async_module_sync():
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


def test_sanitize_url():
    url = "https://www.example.com?q1=value1&q2=value2"
    assert sanitize_url(url, {"q1"}) == "https://www.example.com?q1=value1&q2=REDACTED"
    assert sanitize_url(url, {"q1", "q2"}) == url
    assert sanitize_url(url, {"q2", "q3"}) == "https://www.example.com?q1=REDACTED&q2=value2"
    url = "https://www.example.com"
    assert sanitize_url(url, {"q1", "q3"}) == url
    url = "https://www.example.com?q1=value1"
    assert sanitize_url(url, {"q1", "q3"}) == url
    url = "https://www.example.com?q1=value1&q2="
    assert sanitize_url(url, {"q1", "q3"}) == "https://www.example.com?q1=value1&q2=REDACTED"
    url = "https://www.example.com?q1=value1&q2"
    assert sanitize_url(url, {"q1", "q3"}) == "https://www.example.com?q1=value1&q2"
    url = "https://www.example.com?q1=value1&q2&q3=value3"
    assert sanitize_url(url, {"q1", "q3"}) == "https://www.example.com?q1=value1&q2&q3=value3"
    url = "https://www.example.com?q2=value1&q2=value2"
    assert sanitize_url(url, {"q1", "q3"}) == "https://www.example.com?q2=REDACTED&q2=REDACTED"

    url = "https://www.example.com?REDACTED=foo"
    assert sanitize_url(url, {"q1", "q3"}) == "https://www.example.com?REDACTED=REDACTED"
    url = "https://www.example.com?REDACTED=foo&REDACTED=bar"
    assert sanitize_url(url, {"redacted"}) == "https://www.example.com?REDACTED=foo&REDACTED=bar"
    url = "https://www.example.com?Q1=value1"
    assert sanitize_url(url, {"q3"}) == "https://www.example.com?Q1=REDACTED"

    # Test multiple of the same query parameters.
    url = "https://example.com?q1=value1&q1=value2&q1=value3"
    assert sanitize_url(url, {"q1"}) == "https://example.com?q1=value1&q1=value2&q1=value3"
    assert sanitize_url(url, {"q2"}) == "https://example.com?q1=REDACTED&q1=REDACTED&q1=REDACTED"

    # Test query parameters in the path.
    url = "https://www.example.com/q1=value1/foo"
    assert sanitize_url(url, {"q1", "q3"}) == url
    url = "https://www.example.com/q1=value1&q2=value2/foo"
    assert sanitize_url(url, {"q1", "q3"}) == url

    # Test encoded query parameters.
    url = "https://www.example.com?q1=value%201&q2=value%202&q3=value%203"
    assert sanitize_url(url, {"q1", "q3"}) == "https://www.example.com?q1=value%201&q2=REDACTED&q3=value%203"
    url = "https://www.example.com?q1=value%261&q2=value%262&q3=value%263"
    assert sanitize_url(url, {"q1", "q3"}) == "https://www.example.com?q1=value%261&q2=REDACTED&q3=value%263"
    url = "https://www.example.com?q1=value+1&q2=value+2&q3=value+3"
    assert sanitize_url(url, {"q1", "q3"}) == "https://www.example.com?q1=value+1&q2=REDACTED&q3=value+3"

    # Test case insensitive query parameters.
    url = "https://www.example.com?q1=value1&q2=value2"
    assert sanitize_url(url, {"Q1", "q3"}) == "https://www.example.com?q1=value1&q2=REDACTED"
    url = "https://www.example.com?q1=value1&Q2=value2"
    assert sanitize_url(url, {"Q1", "q2"}) == url

    # Test empty allowed set (all params redacted).
    url = "https://www.example.com?q1=value1&q2=value2"
    assert sanitize_url(url, set()) == "https://www.example.com?q1=REDACTED&q2=REDACTED"

    # Test no-value params are always preserved (nothing to redact).
    url = "https://www.example.com?q1&q2=value2"
    assert sanitize_url(url, {"q1"}) == "https://www.example.com?q1&q2=REDACTED"
    assert sanitize_url(url, {"q2"}) == "https://www.example.com?q1&q2=value2"
    assert sanitize_url(url, set()) == "https://www.example.com?q1&q2=REDACTED"

    url = "https://www.example.com?q1"
    assert sanitize_url(url, set()) == url

    # Test URL with fragment.
    url = "https://www.example.com?q1=value1&q2=value2#fragment"
    assert sanitize_url(url, {"q1"}) == "https://www.example.com?q1=value1&q2=REDACTED#fragment"

    # Test value containing '=' (only first '=' splits key/value).
    url = "https://www.example.com?q1=a=b&q2=value2"
    assert sanitize_url(url, {"q1"}) == "https://www.example.com?q1=a=b&q2=REDACTED"
    assert sanitize_url(url, {"q2"}) == "https://www.example.com?q1=REDACTED&q2=value2"


def test_sanitize_url_with_different_placeholder():
    url = "https://www.example.com?q1=value1&q2=value2"
    assert sanitize_url(url, {"q1"}, "SANITIZED") == "https://www.example.com?q1=value1&q2=SANITIZED"


class TestCaseInsensitiveSet:
    def test_contains(self):
        s = CaseInsensitiveSet(["Foo", "Bar"])
        assert "foo" in s
        assert "FOO" in s
        assert "Foo" in s
        assert "bar" in s
        assert "BAR" in s
        assert "baz" not in s

    def test_add(self):
        s = CaseInsensitiveSet()
        s.add("Foo")
        assert "foo" in s
        assert "FOO" in s
        s.add("bar")
        assert "Bar" in s
        assert len(s) == 2

    def test_discard(self):
        s = CaseInsensitiveSet(["Foo", "Bar"])
        # Discard with different casing should work.
        s.discard("foo")
        assert "foo" not in s
        assert "Foo" not in s
        assert "bar" in s
        # Discard missing item is a no-op.
        s.discard("baz")
        assert "bar" in s
        assert len(s) == 1

    def test_remove(self):
        s = CaseInsensitiveSet(["Foo", "Bar"])
        # Remove with different casing should work.
        s.remove("foo")
        assert "Foo" not in s
        assert "bar" in s
        with pytest.raises(KeyError):
            s.remove("baz")

    def test_update(self):
        s = CaseInsensitiveSet(["Foo"])
        s.update(["Bar", "Baz"])
        assert "bar" in s
        assert "BAZ" in s
        assert len(s) == 3

    def test_clear(self):
        s = CaseInsensitiveSet(["Foo", "Bar"])
        s.clear()
        assert "foo" not in s
        assert len(s) == 0

    def test_pop(self):
        s = CaseInsensitiveSet(["Foo"])
        result = s.pop()
        assert result == "Foo"
        assert "foo" not in s
        assert len(s) == 0

    def test_multiple(self):
        s = CaseInsensitiveSet(["Foo", "foo", "FOO"])
        assert len(s) == 1
        assert "foo" in s
        s.add("FOO")
        assert len(s) == 1
        s.discard("foo")
        assert len(s) == 0
