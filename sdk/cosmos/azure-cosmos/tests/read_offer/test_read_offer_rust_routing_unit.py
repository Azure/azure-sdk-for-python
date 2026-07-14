# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Fast unit tests for the shared rust-routing helpers behind the throughput/offer
read (``get_throughput``, deprecated alias ``read_offer``): the gate, the
prepared-request builder, and the payload parser.

Why these exist: these three helpers decide *whether* a throughput read goes to
the rust engine, *what request* it sends, and *how* it reads the reply back. A
wiring bug in any of them -- routing to rust when a knob isn't supported yet,
sending the wrong query, dropping a guard header, or silently accepting a
malformed reply -- would not crash. It would surface only as a wrong throughput
number in a customer's cost/capacity dashboard, which is the worst way to find
out. These tests lock the wiring down.

What they do, in three groups:

  1. The gate (``can_use_rust_backend_for_read_offer``) -- decides rust vs
     legacy. A rust-backed client with no extra kwargs goes to rust (the binding
     exposes ``read_offer`` / ``read_offer_async``); any extra kwarg, a
     read-timeout, or an availability-strategy keeps the call on the legacy path
     until that knob is mirrored on rust; a core-python client (no backend)
     always stays on legacy.

  2. The builder (``build_read_offer_prepared_request``) -- must produce the
     same offer query the legacy path sends, shaped as a non-partitioned request
     (offers are account-level), and must forward the legacy-prepared headers
     (intended-collection-rid, session token) plus mirror timeout and
     excluded-locations onto the rust request.

  3. The parser (``parse_read_offer_payload``) -- turns the rust
     ``{"Offers":[...]}`` reply back into the exact offer-record list the legacy
     ``QueryOffers`` iterator yields, so ``_deserialize_throughput`` builds the
     identical ``ThroughputProperties`` on either engine. A malformed payload
     must fail with a clear ``ValueError``, not a bare ``KeyError`` / ``TypeError``.

How these differ from the other read_offer tests: the parity tests need a real
account and run both engines to catch *value* drift (wrong RU/s); the ``legacy/``
copies need a real account and run rust only to catch *contract* drift (wrong
object type). These are pure unit tests -- **no emulator, no rust binding, no
account** -- that catch *wiring* drift in the routing helpers before either of
those integration suites even runs.

Run with::

    pytest --noconftest tests/read_offer/test_read_offer_rust_routing_unit.py -v
"""
from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import http_constants
from azure.cosmos import _runtime_constants as runtime_constants
from azure.cosmos._backend.base import BackendResponse, OP_READ_OFFER, OP_TO_BINDING_METHOD
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._offer_rust_routing import (
    build_read_offer_prepared_request,
    can_use_rust_backend_for_read_offer,
    parse_read_offer_payload,
    try_read_offer_with_rust_backend,
    try_read_offer_with_rust_backend_async,
)

_OFFER_QUERY = {
    "query": "SELECT * FROM root r WHERE r.resource=@link",
    "parameters": [{"name": "@link", "value": "dbs/db/colls/coll/"}],
}


def test_gate_is_off_without_backend():
    assert can_use_rust_backend_for_read_offer(backend=None, options={}, kwargs={}) is False


def test_gate_is_on_with_backend_and_no_kwargs():
    # The binding now exposes an offer entry point, so a Rust-backed client with no
    # extra kwargs routes its throughput read through Rust.
    assert can_use_rust_backend_for_read_offer(backend=object(), options={}, kwargs={}) is True


def test_gate_is_off_with_kwargs():
    # Legacy forwards extra kwargs into QueryOffers; keep those on legacy until each
    # knob is mirrored on the Rust path.
    assert (
        can_use_rust_backend_for_read_offer(
            backend=object(), options={}, kwargs={"response_continuation_token_limit_in_kb": 8}
        )
        is False
    )


def test_gate_is_off_with_read_timeout():
    assert (
        can_use_rust_backend_for_read_offer(
            backend=object(),
            options={Constants.Kwargs.READ_TIMEOUT: 5},
            kwargs={},
        )
        is False
    )


def test_gate_is_off_with_availability_strategy():
    assert (
        can_use_rust_backend_for_read_offer(
            backend=object(),
            options={Constants.Kwargs.AVAILABILITY_STRATEGY: True},
            kwargs={},
        )
        is False
    )


def test_op_read_offer_mapped_to_binding_method():
    # The op discriminator is mapped to the binding's `read_offer` function (the
    # async backend appends `_async` to reach `read_offer_async`).
    assert OP_READ_OFFER == "read_offer"
    assert OP_TO_BINDING_METHOD[OP_READ_OFFER] == "read_offer"


def test_builds_prepared_request_as_non_partitioned_query():
    prepared = build_read_offer_prepared_request(
        container_link="/dbs/db/colls/coll/",
        offer_query=_OFFER_QUERY,
        req_headers={
            "x-ms-cosmos-intended-collection-rid": "abc==",
            "x-ms-session-token": "0:-1#1",
        },
        options={},
    )
    assert prepared.op == OP_READ_OFFER
    assert prepared.container_link == "dbs/db/colls/coll"
    # Offers are account-level / non-partitioned.
    assert prepared.partition_key_header == "[]"
    assert prepared.item_id is None
    # The body is the same offer query the legacy path sends.
    assert json.loads(prepared.body_bytes.decode("utf-8")) == _OFFER_QUERY
    # Legacy-prepared headers are forwarded to the Rust prepared request.
    assert prepared.headers.get("x-ms-cosmos-intended-collection-rid") == "abc=="
    assert prepared.headers.get("x-ms-session-token") == "0:-1#1"


def test_prepared_request_mirrors_timeout_and_excluded_locations():
    prepared = build_read_offer_prepared_request(
        container_link="dbs/db/colls/coll",
        offer_query=_OFFER_QUERY,
        req_headers={},
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 12,
        },
    )
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 12


def test_parser_returns_offer_records_unchanged():
    offers = [{"id": "off-1", "offerType": "Invalid", "content": {"offerThroughput": 400}}]
    assert parse_read_offer_payload({"Offers": offers}) == offers


def test_parser_returns_empty_list_for_no_offers():
    assert parse_read_offer_payload({"Offers": []}) == []


def test_parser_rejects_missing_offers_field():
    with pytest.raises(ValueError):
        parse_read_offer_payload({})


def test_parser_rejects_non_list_offers():
    with pytest.raises(ValueError):
        parse_read_offer_payload({"Offers": {"id": "off-1"}})


def test_parser_rejects_non_object_offer_entry():
    with pytest.raises(ValueError):
        parse_read_offer_payload({"Offers": ["not-an-object"]})


def test_try_read_offer_returns_none_when_backend_missing():
    client_connection = SimpleNamespace(_backend=None)
    assert (
        try_read_offer_with_rust_backend(
            client_connection=client_connection,
            container_link="dbs/db/colls/coll",
            offer_query=_OFFER_QUERY,
            options={},
        )
        is None
    )


def test_try_read_offer_executes_backend_with_legacy_prepared_headers(monkeypatch):
    captured = {}
    backend = MagicMock()
    backend.execute.return_value = BackendResponse(
        status_code=200,
        headers={"x-ms-request-charge": "1.0"},
        body=b'{"Offers":[{"id":"off-1","content":{"offerThroughput":400}}]}',
    )
    client_connection = SimpleNamespace(
        _backend=backend,
        default_headers={"x-ms-user-agent": "ua"},
        _query_compatibility_mode="Default",
        last_response_headers=None,
    )

    def _fake_get_headers(_client, headers, *_args):
        captured["input_headers"] = dict(headers)
        result = dict(headers)
        result["x-ms-cosmos-intended-collection-rid"] = "rid-1"
        return result

    def _fake_set_session_token_header(_client, req_headers, _path, _request_params, _options):
        req_headers["x-ms-session-token"] = "0:-1#1"

    monkeypatch.setattr("azure.cosmos._offer_rust_routing.base.GetHeaders", _fake_get_headers)
    monkeypatch.setattr(
        "azure.cosmos._offer_rust_routing.base.set_session_token_header",
        _fake_set_session_token_header,
    )

    offers = try_read_offer_with_rust_backend(
        client_connection=client_connection,
        container_link="dbs/db/colls/coll/",
        offer_query=_OFFER_QUERY,
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 7,
        },
    )

    assert offers == [{"id": "off-1", "content": {"offerThroughput": 400}}]
    assert (
        captured["input_headers"][http_constants.HttpHeaders.ContentType]
        == runtime_constants.MediaTypes.QueryJson
    )
    prepared = backend.execute.call_args.args[0]
    assert prepared.op == OP_READ_OFFER
    assert prepared.partition_key_header == "[]"
    assert prepared.headers["x-ms-cosmos-intended-collection-rid"] == "rid-1"
    assert prepared.headers["x-ms-session-token"] == "0:-1#1"
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 7


@pytest.mark.asyncio
async def test_try_read_offer_async_executes_backend_with_legacy_prepared_headers(monkeypatch):
    captured = {}
    backend = SimpleNamespace()
    backend.execute = AsyncMock(
        return_value=BackendResponse(
            status_code=200,
            headers={"x-ms-request-charge": "1.0"},
            body=b'{"Offers":[{"id":"off-1","content":{"offerThroughput":400}}]}',
        )
    )
    client_connection = SimpleNamespace(
        _backend=backend,
        default_headers={"x-ms-user-agent": "ua"},
        _query_compatibility_mode="Default",
        last_response_headers=None,
    )

    def _fake_get_headers(_client, headers, *_args):
        captured["input_headers"] = dict(headers)
        result = dict(headers)
        result["x-ms-cosmos-intended-collection-rid"] = "rid-1"
        return result

    async def _fake_set_session_token_header_async(_client, req_headers, _path, _request_params, _options):
        req_headers["x-ms-session-token"] = "0:-1#1"

    monkeypatch.setattr("azure.cosmos._offer_rust_routing.base.GetHeaders", _fake_get_headers)
    monkeypatch.setattr(
        "azure.cosmos._offer_rust_routing.base.set_session_token_header_async",
        _fake_set_session_token_header_async,
    )

    offers = await try_read_offer_with_rust_backend_async(
        client_connection=client_connection,
        container_link="dbs/db/colls/coll/",
        offer_query=_OFFER_QUERY,
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 7,
        },
    )

    assert offers == [{"id": "off-1", "content": {"offerThroughput": 400}}]
    assert (
        captured["input_headers"][http_constants.HttpHeaders.ContentType]
        == runtime_constants.MediaTypes.QueryJson
    )
    prepared = backend.execute.await_args.args[0]
    assert prepared.op == OP_READ_OFFER
    assert prepared.partition_key_header == "[]"
    assert prepared.headers["x-ms-cosmos-intended-collection-rid"] == "rid-1"
    assert prepared.headers["x-ms-session-token"] == "0:-1#1"
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 7
