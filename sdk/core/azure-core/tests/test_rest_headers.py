# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import sys

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
from azure.core.rest import HttpRequest

def _get_headers(header_value):
    request = HttpRequest(method="GET", url="http://example.org", headers=header_value)
    return request.headers

def test_headers():
    # headers still can't be list of tuples. Will uncomment once we add this support
    # h = _get_headers([("a", "123"), ("a", "456"), ("b", "789")])
    # assert "a" in h
    # assert "A" in h
    # assert "b" in h
    # assert "B" in h
    # assert "c" not in h
    # assert h["a"] == "123, 456"
    # assert h.get("a") == "123, 456"
    # assert h.get("nope", default=None) is None
    # assert h.get_list("a") == ["123", "456"]

    # assert list(h.keys()) == ["a", "b"]
    # assert list(h.values()) == ["123, 456", "789"]
    # assert list(h.items()) == [("a", "123, 456"), ("b", "789")]
    # assert list(h) == ["a", "b"]
    # assert dict(h) == {"a": "123, 456", "b": "789"}
    # assert repr(h) == "Headers([('a', '123'), ('a', '456'), ('b', '789')])"
    # assert h == [("a", "123"), ("b", "789"), ("a", "456")]
    # assert h == [("a", "123"), ("A", "456"), ("b", "789")]
    # assert h == {"a": "123", "A": "456", "b": "789"}
    # assert h != "a: 123\nA: 456\nb: 789"

    h = _get_headers({"a": "123", "b": "789"})
    assert h["A"] == "123"
    assert h["B"] == "789"


def test_header_mutations():
    h = _get_headers({})
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


def test_headers_insert_retains_ordering():
    h = _get_headers({"a": "a", "b": "b", "c": "c"})
    h["b"] = "123"
    if sys.version_info >= (3, 6):
        assert list(h.values()) == ["a", "123", "c"]
    else:
        assert set(list(h.values())) == set(["a", "123", "c"])


def test_headers_insert_appends_if_new():
    h = _get_headers({"a": "a", "b": "b", "c": "c"})
    h["d"] = "123"
    if sys.version_info >= (3, 6):
        assert list(h.values()) == ["a", "b", "c", "123"]
    else:
        assert set(list(h.values())) == set(["a", "b", "c", "123"])


def test_headers_insert_removes_all_existing():
    h = _get_headers([("a", "123"), ("a", "456")])
    h["a"] = "789"
    assert dict(h) == {"a": "789"}


def test_headers_delete_removes_all_existing():
    h = _get_headers([("a", "123"), ("a", "456")])
    del h["a"]
    assert dict(h) == {}

def test_headers_not_override():
    request = HttpRequest("PUT", "http://example.org", json={"hello": "world"}, headers={"Content-Length": "5000", "Content-Type": "application/my-content-type"})
    assert request.headers["Content-Length"] == "5000"
    assert request.headers["Content-Type"] == "application/my-content-type"

def test_request_headers_case_insensitive():
    request = HttpRequest(
        "PUT",
        "http://example.org",
        headers={
            "Content-Length": 5000,
            "Content-Type": "application/my-content-type"
        }
    )
    assert (
        request.headers["Content-Length"] ==
        request.headers["content-length"] ==
        request.headers["CONTENT-LENGTH"] ==
        request.headers["cOnTEnT-lEngTH"] ==
        5000
    )

    assert(
        request.headers["Content-Type"] ==
        request.headers["content-type"] ==
        request.headers["CONTENT-TYPE"] ==
        request.headers["ConTENt-tYpE"] ==
        "application/my-content-type"
    )

def test_response_headers_case_insensitive(client):
    request = HttpRequest("GET", "/basic/headers")
    response = client.send_request(request)
    response.raise_for_status()
    assert (
        response.headers["lowercase-header"] ==
        response.headers["LOWERCASE-HEADER"] ==
        response.headers["Lowercase-Header"] ==
        response.headers["lOwErCasE-HeADer"] ==
        "lowercase"
    )
    assert (
        response.headers["allcaps-header"] ==
        response.headers["ALLCAPS-HEADER"] ==
        response.headers["Allcaps-Header"] ==
        response.headers["AlLCapS-HeADer"] ==
        "ALLCAPS"
    )
    assert (
        response.headers["camelcase-header"] ==
        response.headers["CAMELCASE-HEADER"] ==
        response.headers["CamelCase-Header"] ==
        response.headers["cAMeLCaSE-hEadER"] ==
        "camelCase"
    )
    return response


# Can't support list of tuples. Will uncomment once we add that support

# def test_multiple_headers():
#     """
#     `Headers.get_list` should support both split_commas=False and split_commas=True.
#     """
#     h = _get_headers([("set-cookie", "a, b"), ("set-cookie", "c")])
#     assert h.get_list("Set-Cookie") == ["a, b", "c"]

#     h = _get_headers([("vary", "a, b"), ("vary", "c")])
#     assert h.get_list("Vary", split_commas=True) == ["a", "b", "c"]