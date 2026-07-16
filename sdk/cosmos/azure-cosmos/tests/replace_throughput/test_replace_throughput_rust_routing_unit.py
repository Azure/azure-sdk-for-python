# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Fast unit tests for the shared rust-routing helpers behind the throughput
*change* (``replace_throughput``): the gate, the prepared-request builder, and the
offer-PUT executor.

Why these exist: ``replace_throughput`` is a read-modify-write on the container's
one offer record -- read the current offer, change the RU/s in it, and PUT it back.
These helpers decide *whether* the change goes to the rust engine, *which* offer it
overwrites, and *what* it sends. A wiring bug here would not crash; it would send
the change to the wrong offer, drop a guard header, or fail to read the applied RU/s
back -- a customer would set 50,000 RU/s and either it wouldn't take or they
couldn't confirm it did, at the worst possible moment (a sale, the monthly bill).
These tests lock the wiring down with no account and no rust binding.

Three groups:

  1. The gate (``can_use_rust_backend_for_replace_throughput``) -- decides rust vs
     legacy. It mirrors the read gate: a rust-backed client with no extra kwargs
     goes to rust; a ``read_timeout`` (socket read timeout), an
     ``availability_strategy`` (cross-region hedging), or any other
     extra kwarg keeps the whole call on legacy; a core-python client (no backend)
     always stays on legacy.

  2. The builder (``build_replace_offer_prepared_request``) -- must produce a
     non-partitioned request (offers are account-level) carrying the full mutated
     offer document as the body and the offer RID in ``item_id`` (which offer to
     overwrite), and must forward the legacy-prepared headers plus mirror timeout
     and excluded-locations.

  3. The executor (``try_replace_offer_with_rust_backend``) -- derives the offer RID
     from the offer's ``_self`` link, runs the PUT on the rust backend, and returns
     the updated offer so the caller can read the applied RU/s back. With no backend
     it returns ``None`` so the caller falls back to legacy.

Run with::

    pytest --noconftest tests/replace_throughput/test_replace_throughput_rust_routing_unit.py -v
"""
from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import _base as base
from azure.cosmos._backend.base import BackendResponse, OP_REPLACE_OFFER, OP_TO_BINDING_METHOD
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._offer_rust_routing import (
    build_replace_offer_prepared_request,
    can_use_rust_backend_for_replace_throughput,
    try_replace_offer_with_rust_backend,
    try_replace_offer_with_rust_backend_async,
)

# A manual (fixed-RU/s) offer record, shaped exactly like the service returns it.
_OFFER = {
    "id": "off-1",
    "_rid": "AAAAAA==",
    "_self": "offers/AAAAAA==/",
    "offerVersion": "V2",
    "resource": "dbs/db/colls/coll/",
    "content": {"offerThroughput": 500},
}


def test_gate_is_off_without_backend():
    assert (
        can_use_rust_backend_for_replace_throughput(backend=None, options={}, kwargs={})
        is False
    )


def test_gate_is_on_with_backend_and_no_kwargs():
    assert (
        can_use_rust_backend_for_replace_throughput(backend=object(), options={}, kwargs={})
        is True
    )


def test_gate_is_off_with_kwargs():
    assert (
        can_use_rust_backend_for_replace_throughput(
            backend=object(), options={}, kwargs={"some_unmirrored_knob": 1}
        )
        is False
    )


def test_gate_is_off_with_read_timeout():
    # read_timeout (socket read timeout) is a known driver-side gap.
    assert (
        can_use_rust_backend_for_replace_throughput(
            backend=object(),
            options={Constants.Kwargs.READ_TIMEOUT: 5},
            kwargs={},
        )
        is False
    )


def test_gate_is_off_with_availability_strategy():
    # availability_strategy (cross-region hedging) is a known driver-side gap.
    assert (
        can_use_rust_backend_for_replace_throughput(
            backend=object(),
            options={Constants.Kwargs.AVAILABILITY_STRATEGY: True},
            kwargs={},
        )
        is False
    )


def test_op_replace_offer_mapped_to_binding_method():
    # The op discriminator maps to the binding's `replace_offer` function (the async
    # backend appends `_async` to reach `replace_offer_async`).
    assert OP_REPLACE_OFFER == "replace_offer"
    assert OP_TO_BINDING_METHOD[OP_REPLACE_OFFER] == "replace_offer"


def test_builds_prepared_request_as_non_partitioned_offer_put():
    prepared = build_replace_offer_prepared_request(
        container_link="/dbs/db/colls/coll/",
        offer=_OFFER,
        offer_id="AAAAAA==",
        req_headers={
            "x-ms-cosmos-intended-collection-rid": "abc==",
            "x-ms-session-token": "0:-1#1",
        },
        options={},
    )
    assert prepared.op == OP_REPLACE_OFFER
    assert prepared.container_link == "dbs/db/colls/coll"
    # Offers are account-level / non-partitioned.
    assert prepared.partition_key_header == "[]"
    # The offer RID says which offer to overwrite.
    assert prepared.item_id == "AAAAAA=="
    # The body is the full mutated offer document.
    assert json.loads(prepared.body_bytes.decode("utf-8")) == _OFFER
    # Legacy-prepared headers are forwarded to the Rust prepared request.
    assert prepared.headers.get("x-ms-cosmos-intended-collection-rid") == "abc=="
    assert prepared.headers.get("x-ms-session-token") == "0:-1#1"


def test_prepared_request_mirrors_timeout_and_excluded_locations():
    prepared = build_replace_offer_prepared_request(
        container_link="dbs/db/colls/coll",
        offer=_OFFER,
        offer_id="AAAAAA==",
        req_headers={},
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 12,
        },
    )
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 12


def test_try_replace_offer_returns_none_when_backend_missing():
    client_connection = SimpleNamespace(_backend=None)
    assert (
        try_replace_offer_with_rust_backend(
            client_connection=client_connection,
            container_link="dbs/db/colls/coll",
            offer=_OFFER,
            options={},
        )
        is None
    )


def test_try_replace_offer_executes_backend_and_targets_offer_rid(monkeypatch):
    backend = MagicMock()
    # Replace returns the single updated offer document (not a feed envelope).
    backend.execute.return_value = BackendResponse(
        status_code=200,
        headers={"x-ms-request-charge": "1.0"},
        body=b'{"id":"off-1","_self":"offers/AAAAAA==/","content":{"offerThroughput":500}}',
    )
    client_connection = SimpleNamespace(
        _backend=backend,
        default_headers={"x-ms-user-agent": "ua"},
        last_response_headers=None,
    )

    def _fake_get_headers(_client, headers, *_args):
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

    data = try_replace_offer_with_rust_backend(
        client_connection=client_connection,
        container_link="dbs/db/colls/coll/",
        offer=_OFFER,
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 7,
        },
    )

    # The updated offer comes back with the applied RU/s.
    assert data["content"]["offerThroughput"] == 500
    prepared = backend.execute.call_args.args[0]
    assert prepared.op == OP_REPLACE_OFFER
    assert prepared.partition_key_header == "[]"
    # The offer RID targeted by the PUT is derived from the offer's _self link.
    assert prepared.item_id == base.GetResourceIdOrFullNameFromLink(_OFFER["_self"])
    assert prepared.headers["x-ms-cosmos-intended-collection-rid"] == "rid-1"
    assert prepared.headers["x-ms-session-token"] == "0:-1#1"
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 7


@pytest.mark.asyncio
async def test_try_replace_offer_async_executes_backend_and_targets_offer_rid(monkeypatch):
    backend = SimpleNamespace()
    backend.execute = AsyncMock(
        return_value=BackendResponse(
            status_code=200,
            headers={"x-ms-request-charge": "1.0"},
            body=b'{"id":"off-1","_self":"offers/AAAAAA==/","content":{"offerThroughput":500}}',
        )
    )
    client_connection = SimpleNamespace(
        _backend=backend,
        default_headers={"x-ms-user-agent": "ua"},
        last_response_headers=None,
    )

    def _fake_get_headers(_client, headers, *_args):
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

    data = await try_replace_offer_with_rust_backend_async(
        client_connection=client_connection,
        container_link="dbs/db/colls/coll/",
        offer=_OFFER,
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 7,
        },
    )

    assert data["content"]["offerThroughput"] == 500
    prepared = backend.execute.await_args.args[0]
    assert prepared.op == OP_REPLACE_OFFER
    assert prepared.partition_key_header == "[]"
    assert prepared.item_id == base.GetResourceIdOrFullNameFromLink(_OFFER["_self"])
    assert prepared.headers["x-ms-cosmos-intended-collection-rid"] == "rid-1"
    assert prepared.headers["x-ms-session-token"] == "0:-1#1"
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 7
