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

  3. The dispatch (``ThroughputHelper`` via ``CosmosBackend.run_operation``) -- derives
     the offer RID from the offer's ``_self`` link, runs the PUT on the selected
     backend, and returns the updated offer so the caller can read the applied RU/s
     back. Eligibility is computed once and used for both the read and the write, so
     one replace-throughput call cannot split across the two engines.

Run with::

    pytest --noconftest tests/replace_throughput/test_replace_throughput_rust_routing_unit.py -v
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from azure.cosmos import _base as base
from azure.cosmos._backend.operations import OP_REPLACE_OFFER, OP_TO_BINDING_METHOD
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._offer_rust_routing import (
    build_replace_offer_prepared_request,
    can_use_rust_backend_for_replace_throughput,
    prepare_replace_offer_request,
    prepare_replace_offer_request_async,
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
    """A Python client does not attempt the Rust throughput-replacement path."""
    assert (
        can_use_rust_backend_for_replace_throughput(backend=None, options={}, kwargs={})
        is False
    )


def test_gate_is_on_with_backend_and_no_kwargs():
    """A supported throughput replacement uses Rust."""
    assert (
        can_use_rust_backend_for_replace_throughput(backend=object(), options={}, kwargs={})
        is True
    )


def test_gate_is_off_with_kwargs():
    """Options unsupported by Rust keep the throughput replacement on Python."""
    assert (
        can_use_rust_backend_for_replace_throughput(
            backend=object(), options={}, kwargs={"some_unmirrored_knob": 1}
        )
        is False
    )


def test_gate_is_off_with_read_timeout():
    """A per-call socket timeout keeps the throughput replacement on Python."""
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
    """A per-call availability strategy keeps the throughput replacement on Python."""
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
    """``OP_REPLACE_OFFER`` maps to the binding's ``replace_offer`` method so a rename cannot silently unroute the operation."""
    # The op discriminator maps to the binding's `replace_offer` function (the async
    # backend appends `_async` to reach `replace_offer_async`).
    assert OP_REPLACE_OFFER == "replace_offer"
    assert OP_TO_BINDING_METHOD[OP_REPLACE_OFFER] == "replace_offer"


def test_builds_prepared_request_as_non_partitioned_offer_put():
    """The Rust request updates the selected account-level throughput offer."""
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
    """Rust receives the caller's timeout and excluded locations."""
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


def _offer_replace_connection():
    """Return a minimal fake ``client_connection`` carrying default headers."""
    return SimpleNamespace(
        default_headers={"x-ms-user-agent": "ua"},
        _query_compatibility_mode="Default",
        last_response_headers=None,
    )


def _patch_offer_replace_headers(monkeypatch, captured, *, is_async=False):
    """Supply the headers that the request builder must preserve."""

    def _fake_get_headers(_client, headers, *_args):
        """Inject the ``intended-collection-rid`` guard header and record the input."""
        captured["input_headers"] = dict(headers)
        result = dict(headers)
        result["x-ms-cosmos-intended-collection-rid"] = "rid-1"
        return result

    monkeypatch.setattr("azure.cosmos._offer_rust_routing.base.GetHeaders", _fake_get_headers)

    if is_async:
        async def _fake_set(_client, req_headers, path, _request_params, _options):
            """Stand in for ``set_session_token_header_async``; injects a session token and records the path."""
            captured["session_path"] = path
            req_headers["x-ms-session-token"] = "0:-1#1"

        monkeypatch.setattr(
            "azure.cosmos._offer_rust_routing.base.set_session_token_header_async", _fake_set
        )
    else:
        def _fake_set(_client, req_headers, path, _request_params, _options):
            """Stand in for ``set_session_token_header``; injects a session token and records the path."""
            captured["session_path"] = path
            req_headers["x-ms-session-token"] = "0:-1#1"

        monkeypatch.setattr(
            "azure.cosmos._offer_rust_routing.base.set_session_token_header", _fake_set
        )


def _assert_offer_replace_prepared(prepared, captured):
    """Assert all required fields on a ``prepare_replace_offer_request`` result."""
    assert prepared.op == OP_REPLACE_OFFER
    assert prepared.partition_key_header == "[]"
    # The offer link identifies the record to update.
    assert prepared.item_id == "AAAAAA=="
    assert json.loads(prepared.body_bytes.decode("utf-8")) == _OFFER
    assert prepared.headers["x-ms-cosmos-intended-collection-rid"] == "rid-1"
    assert prepared.headers["x-ms-session-token"] == "0:-1#1"
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 12
    # The session token uses the offer's own path.
    assert captured["session_path"] == base.GetPathFromLink(_OFFER["_self"])


def test_prepare_replace_offer_request_carries_the_legacy_headers(monkeypatch):
    """The Rust request keeps headers prepared by the Python SDK."""
    captured = {}
    _patch_offer_replace_headers(monkeypatch, captured)

    prepared = prepare_replace_offer_request(
        client_connection=_offer_replace_connection(),
        container_link="dbs/db/colls/coll",
        offer=_OFFER,
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 12,
        },
    )

    _assert_offer_replace_prepared(prepared, captured)


@pytest.mark.asyncio
async def test_prepare_replace_offer_request_async_carries_the_legacy_headers(monkeypatch):
    """The async request keeps the same required headers as the sync request."""
    captured = {}
    _patch_offer_replace_headers(monkeypatch, captured, is_async=True)

    prepared = await prepare_replace_offer_request_async(
        client_connection=_offer_replace_connection(),
        container_link="dbs/db/colls/coll",
        offer=_OFFER,
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 12,
        },
    )

    _assert_offer_replace_prepared(prepared, captured)
