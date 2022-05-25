# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import platform
from azure.core.rest import HttpRequest
import aiohttp
from azure.core.rest._aiohttp import RestAioHttpTransportResponse

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
    async def _get_response_headers(request):
        response = await client.send_request(request)
        response.raise_for_status
        for header in RESPONSE_HEADERS_TO_IGNORE:
            response.headers.pop(header, None)
        return response.headers
    return _get_response_headers

@pytest.mark.asyncio
async def test_headers_response(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
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

    assert list(h.keys()) == ["a", "b"]
    assert list(h.values()) == ["123, 456", "789"]
    assert list(h.items()) == [("a", "123, 456"), ("b", "789")]
    assert list(h) == ["a", "b"]
    assert dict(h) == {"a": "123, 456", "b": "789"}

@pytest.mark.asyncio
async def test_headers_response_keys(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # basically want to make sure this behaves like dict {"a": "123, 456", "b": "789"}
    ref_dict = {"a": "123, 456", "b": "789"}
    assert list(h.keys()) == list(ref_dict.keys())
    assert repr(h.keys()) == repr(ref_dict.keys())
    assert "a" in h.keys()
    assert "A" in h.keys()
    assert "b" in h.keys()
    assert "B" in h.keys()
    assert set(h.keys()) == set(ref_dict.keys())

@pytest.mark.skipif(platform.python_implementation() == 'PyPy', reason="https://github.com/aio-libs/aiohttp/issues/5967")
@pytest.mark.asyncio
async def test_headers_response_keys_mutability(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # test mutability
    before_mutation_keys = h.keys()
    h['c'] = '000'
    assert 'c' in before_mutation_keys

@pytest.mark.asyncio
async def test_headers_response_values(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # basically want to make sure this behaves like dict {"a": "123, 456", "b": "789"}
    ref_dict = {"a": "123, 456", "b": "789"}
    assert list(h.values()) == list(ref_dict.values())
    assert repr(h.values()) == repr(ref_dict.values())
    assert '123, 456' in h.values()
    assert '789' in h.values()
    assert set(h.values()) == set(ref_dict.values())

@pytest.mark.skipif(platform.python_implementation() == 'PyPy', reason="https://github.com/aio-libs/aiohttp/issues/5967")
@pytest.mark.asyncio
async def test_headers_response_values_mutability(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # test mutability
    before_mutation_values = h.values()
    h['c'] = '000'
    assert '000' in before_mutation_values

@pytest.mark.asyncio
async def test_headers_response_items(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # basically want to make sure this behaves like dict {"a": "123, 456", "b": "789"}
    ref_dict = {"a": "123, 456", "b": "789"}
    assert list(h.items()) == list(ref_dict.items())
    assert repr(h.items()) == repr(ref_dict.items())
    assert ("a", '123, 456') in h.items()
    assert not ("a", '123, 456', '123, 456') in h.items()
    assert not {"a": "blah", "123, 456": "blah"} in h.items()
    assert ("A", '123, 456') in h.items()
    assert ("b", '789') in h.items()
    assert ("B", '789') in h.items()
    assert set(h.items()) == set(ref_dict.items())

@pytest.mark.skipif(platform.python_implementation() == 'PyPy', reason="https://github.com/aio-libs/aiohttp/issues/5967")
@pytest.mark.asyncio
async def test_headers_response_items_mutability(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    # test mutability
    before_mutation_items = h.items()
    h['c'] = '000'
    assert ('c', '000') in before_mutation_items

@pytest.mark.asyncio
async def test_header_mutations(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/empty"))
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

@pytest.mark.asyncio
async def test_copy_headers_method(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/case-insensitive"))
    headers_copy = h.copy()
    assert h == headers_copy
    assert h is not headers_copy

@pytest.mark.asyncio
async def test_headers_insert_retains_ordering(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/ordered"))
    h["b"] = "123"
    assert list(h.values()) == ["a", "123", "c"]

@pytest.mark.asyncio
async def test_headers_insert_appends_if_new(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/case-insensitive"))
    h["d"] = "123"
    assert list(h.values()) == ["lowercase", "ALLCAPS", "camelCase", "123"]

@pytest.mark.asyncio
async def test_headers_insert_removes_all_existing(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    h["a"] = "789"
    assert dict(h) == {"a": "789", "b": "789"}

@pytest.mark.asyncio
async def test_headers_delete_removes_all_existing(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/numbers"))
    del h["a"]
    assert dict(h) == {"b": "789"}

@pytest.mark.asyncio
async def test_response_headers_case_insensitive(client):
    request = HttpRequest("GET", "/headers/case-insensitive")
    response = await client.send_request(request)
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

@pytest.mark.asyncio
async def test_multiple_headers_duplicate_case_insensitive(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/case-insensitive"))
    assert (
        h["Duplicate-Header"] ==
        h['duplicate-header'] ==
        h['DupLicAte-HeaDER'] ==
        "one, two, three"
    )

@pytest.mark.asyncio
async def test_multiple_headers_commas(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/commas"))
    assert h["Set-Cookie"] == "a,  b, c"

@pytest.mark.asyncio
async def test_update(get_response_headers):
    h = await get_response_headers(HttpRequest("GET", "/headers/duplicate/commas"))
    assert h["Set-Cookie"] == "a,  b, c"
    h.update({"Set-Cookie": "override", "new-key": "new-value"})
    assert h['Set-Cookie'] == 'override'
    assert h["new-key"] == "new-value"
