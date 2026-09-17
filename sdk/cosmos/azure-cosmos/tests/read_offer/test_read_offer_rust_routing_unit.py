# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offer routing, direct request preparation and payload contracts; no network."""

from __future__ import annotations
from common.typed_requests import legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings

from copy import deepcopy
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.cosmos import _base
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._backend.operations import OP_READ_OFFER, OP_TO_BINDING_METHOD
from azure.cosmos._helpers._request_settings import (
    HEADERS_THE_DRIVER_REGENERATES,
    HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE,
)
from azure.cosmos._helpers._request_offer import build_read_offer_request, build_replace_offer_request
from azure.cosmos._offer_rust_routing import can_use_rust_backend_for_read_offer, parse_read_offer_payload, build_read_offer_from_connection

RUST_BACKEND = SimpleNamespace(name="rust")
_OFFER_QUERY = {
    "query": "SELECT * FROM root r WHERE r.resource=@link",
    "parameters": [{"name": "@link", "value": "dbs/db/colls/coll/"}],
}


@pytest.mark.parametrize(
    "backend,options,kwargs,expected",
    [
        (LEGACY_BACKEND, {}, {}, False),
        (RUST_BACKEND, {}, {}, True),
        (RUST_BACKEND, {}, {"unknown": 1}, False),
        (RUST_BACKEND, {"read_timeout": 5}, {}, False),
        (RUST_BACKEND, {"availabilityStrategy": True}, {}, False),
    ],
)
def test_offer_read_gate(backend, options, kwargs, expected):
    assert can_use_rust_backend_for_read_offer(backend=backend, options=options, kwargs=kwargs) is expected


@pytest.mark.parametrize("header", sorted(HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE))
def test_offer_read_refuses_customer_overrides(header):
    assert not can_use_rust_backend_for_read_offer(
        backend=RUST_BACKEND,
        options={"initialHeaders": {header.upper(): "custom"}},
        kwargs={},
    )


def test_header_policies_remain_distinct():
    assert HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE == {
        "accept",
        "cache-control",
        "user-agent",
        "x-ms-version",
    }
    assert HEADERS_THE_DRIVER_REGENERATES - HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE == {
        "authorization",
        "content-type",
        "x-ms-date",
    }
    assert not {"x-ms-activity-id", "x-ms-session-token"} & HEADERS_THE_DRIVER_REGENERATES


@pytest.mark.parametrize("resource_link", ["dbs/db", "/dbs/db/colls/coll/"])
def test_offer_read_preparation_never_uses_legacy_transport(monkeypatch, resource_link):
    forbidden = MagicMock(side_effect=AssertionError("legacy preparation must not run"))
    for name in (
        "GetHeaders",
        "set_session_token_header",
        "set_session_token_header_async",
        "_get_authorization_header",
        "GenerateGuidId",
    ):
        monkeypatch.setattr(_base, name, forbidden)
    defaults = {
        **{name.upper(): "SDK default" for name in HEADERS_THE_DRIVER_REGENERATES},
        "x-ms-consistency-level": "Session",
        "x-ms-cosmos-throughput-bucket": "1",
        "x-ms-activity-id": "default-activity",
    }
    options = {
        "containerRID": "owner-rid",
        "excludedLocations": ["West US"],
        "timeout": 7,
        "throughputBucket": 3,
        "sessionToken": "master-resources-ignore-this",
        "initialHeaders": {
            "X-MS-ACTIVITY-ID": "caller-activity",
            "X-MS-SESSION-TOKEN": "raw-session",
            "X-Custom": "retained",
            "X-MS-COSMOS-THROUGHPUT-BUCKET": "2",
        },
    }
    original = deepcopy((defaults, options, _OFFER_QUERY))
    connection = SimpleNamespace(default_headers=defaults)
    kwargs = dict(client_connection=connection, container_link=resource_link, offer_query=_OFFER_QUERY, options=options)
    prepared = build_read_offer_from_connection(**kwargs)
    forbidden.assert_not_called()
    assert (defaults, options, _OFFER_QUERY) == original
    assert prepared.op == OP_READ_OFFER == OP_TO_BINDING_METHOD[OP_READ_OFFER]
    assert prepared.container_link == resource_link.strip("/")
    assert legacy_partition_key_from_request(prepared) == "[]"
    assert prepared.item_id is None
    assert json.loads(prepared.body_bytes) == _OFFER_QUERY
    assert wire_headers(prepared) == {
        "x-ms-consistency-level": "Session",
        "x-ms-cosmos-throughput-bucket": "3",
        "x-ms-activity-id": "caller-activity",
        "x-ms-session-token": "raw-session",
        "x-custom": "retained",
        "x-ms-cosmos-intended-collection-rid": "owner-rid",
    }
    assert settings_options(prepared) == {"excludedLocations": ["West US"], "timeout_seconds": 7}


def test_offer_builder_does_not_mint_activity_or_session_headers():
    prepared = build_read_offer_request(
        resource_link="dbs/db",
        offer_query=_OFFER_QUERY,
        request_options={},
        default_headers={},
    )
    assert wire_headers(prepared) == {}


@pytest.mark.parametrize("initial_headers", [[], False, "header"])
def test_offer_builder_rejects_invalid_initial_headers(initial_headers):
    with pytest.raises(TypeError, match="initial_headers must be a mapping"):
        build_read_offer_request(
            resource_link="dbs/db", offer_query=_OFFER_QUERY,
            request_options={"initialHeaders": initial_headers}, default_headers={},
        )


@pytest.mark.parametrize("payload", [{}, {"Offers": {}}, {"Offers": ["invalid"]}])
def test_offer_parser_rejects_malformed_payload(payload):
    with pytest.raises(ValueError, match="read_offer Rust payload"):
        parse_read_offer_payload(payload)


@pytest.mark.parametrize("offers", [[], [{"id": "offer", "content": {"offerThroughput": 400}}]])
def test_offer_parser_preserves_records(offers):
    assert parse_read_offer_payload({"Offers": offers}) == offers


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("replace_offer", [False, True])
def test_native_offer_entries_accept_direct_requests_before_io(monkeypatch, is_async, replace_offer):
    native = pytest.importorskip("azure.cosmos._rust")
    monkeypatch.setenv("COSMOS_WIRE_STRICT", "1")
    kwargs = {
        "resource_link": "dbs/db",
        "request_options": {
            "initialHeaders": {"x-customer": "value", "x-ms-activity-id": "caller"},
            "timeout": 3,
            "excludedLocations": ["West US"],
        },
        "default_headers": {"User-Agent": "SDK default"},
    }
    if replace_offer:
        prepared = build_replace_offer_request(
            offer_body={"_self": "offers/offer-rid/", "content": {"offerThroughput": 500}},
            **kwargs,
        )
    else:
        prepared = build_read_offer_request(offer_query=_OFFER_QUERY, **kwargs)
    entrypoint = getattr(native, prepared.op + ("_async" if is_async else ""))
    # Extraction runs before handle lookup. This verifies the real ABI and strict
    # request parser without creating a driver or contacting an account.
    with pytest.raises(RuntimeError, match="no driver registered for handle"):
        entrypoint("unused-direct-offer-test-handle", prepared)
