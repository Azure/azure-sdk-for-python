# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import sys
from requests import Response
import pytest
from azure.core.rest._requests_basic import RestRequestsTransportResponse

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
from azure.core.rest import HttpRequest

@pytest.fixture
def get_request_headers():
    def _get_request_headers(header_value):
        request = HttpRequest(method="GET", url="http://example.org", headers=header_value)
        return request.headers
    return _get_request_headers

# flask returns these response headers, which we don't really need for these following tests
RESPONSE_HEADERS_TO_IGNORE = [
    "Connection",
    "Content-Type",
    "Content-Length",
    "Server",
    "Date",
]

@pytest.fixture
def get_response_headers(client):
    def _get_response_headers(request):
        response = client.send_request(request)
        response.raise_for_status
        for header in RESPONSE_HEADERS_TO_IGNORE:
            response.headers.pop(header, None)
        return response.headers
    return _get_response_headers

def test_headers_request(get_request_headers):
    h = get_request_headers({"a": "123", "b": "789"})
    assert h["A"] == "123"
    assert h["B"] == "789"

def test_headers_response(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    assert "a" in h
    assert "A" in h
    assert "b" in h
    assert "B" in h
    assert "c" not in h
    assert h["a"] == "123, 456"
    assert h["A"] == "123, 456"
    assert h.get("a") == "123, 456"
    assert h.get("A") == "123, 456"
    assert h.get("nope") is None
    assert h.get("nope", default="default") is "default"
    assert h.get("nope", default=None) is None
    assert h.get("nope", default=[]) == []
    assert list(h) == ['a', 'b']

    assert set(h.keys()) == set(["a", "b"])
    assert list(h.values()) == ["123, 456", "789"]
    assert list(h.items()) == [("a", "123, 456"), ("b", "789")]
    assert list(h) == ["a", "b"]
    assert dict(h) == {"a": "123, 456", "b": "789"}

def test_headers_response_keys(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # basically want to make sure this behaves like dict {"a": "123, 456", "b": "789"}
    ref_dict = {"a": "123, 456", "b": "789"}
    assert set(h.keys()) == set(ref_dict.keys())
    if sys.version_info > (3, 0):
        # repr is unruly for 2.7
        assert repr(h.keys()) == "KeysView({'a': '123, 456', 'b': '789'})"
    assert "a" in h.keys()
    assert "b" in h.keys()
    assert set(h.keys()) == set(ref_dict.keys())

@pytest.mark.skipif(sys.version_info < (3, 0),
                    reason="In 2.7, .keys() are not mutable")
def test_headers_response_keys_mutability(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # test mutability
    before_mutation_keys = h.keys()
    h['c'] = '000'
    assert 'c' in before_mutation_keys

def test_headers_response_values(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # basically want to make sure this behaves like dict {"a": "123, 456", "b": "789"}
    ref_dict = {"a": "123, 456", "b": "789"}
    assert set(h.values()) == set(ref_dict.values())
    if sys.version_info > (3, 0):
        # repr is unruly for 2.7
        assert repr(h.values()) == "ValuesView({'a': '123, 456', 'b': '789'})"
    assert '123, 456' in h.values()
    assert '789' in h.values()
    assert set(h.values()) == set(ref_dict.values())

@pytest.mark.skipif(sys.version_info < (3, 0),
                    reason="In 2.7, .values() are not mutable")
def test_headers_response_values_mutability(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # test mutability
    before_mutation_values = h.values()
    h['c'] = '000'
    assert '000' in before_mutation_values

def test_headers_response_items(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # basically want to make sure this behaves like dict {"a": "123, 456", "b": "789"}
    ref_dict = {"a": "123, 456", "b": "789"}
    assert set(h.items()) == set(ref_dict.items())
    if sys.version_info > (3, 0):
        # repr is unruly for 2.7
        assert repr(h.items()) == "ItemsView({'a': '123, 456', 'b': '789'})"
    assert ("a", '123, 456') in h.items()
    assert not ("a", '123, 456', '123, 456') in h.items()
    assert not {"a": "blah", "123, 456": "blah"} in h.items()
    assert ("A", '123, 456') in h.items()
    assert ("b", '789') in h.items()
    assert ("B", '789') in h.items()
    assert set(h.items()) == set(ref_dict.items())


@pytest.mark.skipif(sys.version_info < (3, 0),
                    reason="In 2.7, .items() are not mutable")
def test_headers_response_items_mutability(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # test mutability
    before_mutation_items = h.items()
    h['c'] = '000'
    assert ('c', '000') in before_mutation_items

def test_header_mutations(get_request_headers, get_response_headers):
    def _headers_check(h):
        assert dict(h) == {}
        h["a"] = "1"
        assert dict(h) == {"a": "1"}
        h["a"] = "2"
        assert dict(h) == {"a": "2"}
        h.setdefault("a", "3")
        assert dict(h) == {"a": "2"}
        h.setdefault("b", "4")
        assert dict(h) == {"a": "2", "b": "4"}
        del h["a"]
        assert dict(h) == {"b": "4"}
    _headers_check(get_request_headers({}))
    _headers_check(get_response_headers(HttpRequest("GET", "/headers/empty")))

def test_copy_headers_method(get_request_headers, get_response_headers):
    def _header_check(h):
        headers_copy = h.copy()
        assert h == headers_copy
        assert h is not headers_copy
    _header_check(get_request_headers({
        "lowercase-header": "lowercase",
        "ALLCAPS-HEADER": "ALLCAPS",
        "CamelCase-Header": "camelCase",
    }))
    _header_check(get_response_headers(HttpRequest("GET", "/headers/case-insensitive")))

def test_headers_insert_retains_ordering(get_request_headers, get_response_headers):
    def _header_check(h):
        h["b"] = "123"
        if sys.version_info >= (3, 6):
            assert list(h.values()) == ["a", "123", "c"]
        else:
            assert set(h.values()) == set(["a", "123", "c"])
    _header_check(get_request_headers({"a": "a", "b": "b", "c": "c"}))
    _header_check(get_response_headers(HttpRequest("GET", "/headers/ordered")))


def test_headers_insert_appends_if_new(get_request_headers, get_response_headers):
    def _headers_check(h):
        h["d"] = "123"
        if sys.version_info >= (3, 6):
            assert list(h.values()) == ["lowercase", "ALLCAPS", "camelCase", "123"]
        else:
            assert set(list(h.values())) == set(["lowercase", "ALLCAPS", "camelCase", "123"])
    _headers_check(get_request_headers({
        "lowercase-header": "lowercase",
        "ALLCAPS-HEADER": "ALLCAPS",
        "CamelCase-Header": "camelCase",
    }))
    _headers_check(get_response_headers(HttpRequest("GET", "/headers/case-insensitive")))


def test_headers_insert_removes_all_existing(get_request_headers, get_response_headers):
    def _headers_check(h):
        h["a"] = "789"
        assert dict(h) == {"a": "789", "b": "789"}
    _headers_check(get_request_headers([("a", "123"), ("a", "456"), ("b", "789")]))
    _headers_check(get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers")))


def test_headers_delete_removes_all_existing(get_request_headers, get_response_headers):
    def _headers_check(h):
        del h["a"]
        assert dict(h) == {"b": "789"}
    _headers_check(get_request_headers([("a", "123"), ("a", "456"), ("b", "789")]))
    _headers_check(get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers")))

def test_headers_not_override():
    request = HttpRequest("PUT", "http://example.org", json={"hello": "world"}, headers={"Content-Length": "5000", "Content-Type": "application/my-content-type"})
    assert request.headers["Content-Length"] == "5000"
    assert request.headers["Content-Type"] == "application/my-content-type"

def test_headers_case_insensitive(get_request_headers, get_response_headers):
    def _headers_check(h):
        assert (
            h["lowercase-header"] ==
            h["LOWERCASE-HEADER"] ==
            h["Lowercase-Header"] ==
            h["lOwErCasE-HeADer"] ==
            "lowercase"
        )
        assert (
            h["allcaps-header"] ==
            h["ALLCAPS-HEADER"] ==
            h["Allcaps-Header"] ==
            h["AlLCapS-HeADer"] ==
            "ALLCAPS"
        )
        assert (
            h["camelcase-header"] ==
            h["CAMELCASE-HEADER"] ==
            h["CamelCase-Header"] ==
            h["cAMeLCaSE-hEadER"] ==
            "camelCase"
        )
    _headers_check(get_request_headers({
        "lowercase-header": "lowercase",
        "ALLCAPS-HEADER": "ALLCAPS",
        "CamelCase-Header": "camelCase",
    }))
    _headers_check(get_response_headers(HttpRequest("GET", "/headers/case-insensitive")))

def test_multiple_headers_duplicate_case_insensitive(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/case-insensitive"))
    assert (
        h["Duplicate-Header"] ==
        h['duplicate-header'] ==
        h['DupLicAte-HeaDER'] ==
        "one, two, three"
    )

def test_multiple_headers_commas(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/commas"))
    assert h["Set-Cookie"] == "a,  b, c"

def test_update(get_response_headers):
    h = get_response_headers(HttpRequest("GET", "/headers/duplicate/commas"))
    assert h["Set-Cookie"] == "a,  b, c"
    h.update({"Set-Cookie": "override", "new-key": "new-value"})
    assert h['Set-Cookie'] == 'override'
    assert h["new-key"] == "new-value"
