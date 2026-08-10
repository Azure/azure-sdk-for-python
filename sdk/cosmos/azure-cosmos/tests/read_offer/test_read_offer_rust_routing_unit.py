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

import pytest

from azure.cosmos import http_constants
from azure.cosmos import _runtime_constants as runtime_constants
from azure.cosmos._backend.operations import OP_READ_OFFER, OP_TO_BINDING_METHOD
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._offer_rust_routing import (
    build_read_offer_prepared_request,
    can_use_rust_backend_for_read_offer,
    parse_read_offer_payload,
    prepare_read_offer_request,
    prepare_read_offer_request_async,
)

_OFFER_QUERY = {
    "query": "SELECT * FROM root r WHERE r.resource=@link",
    "parameters": [{"name": "@link", "value": "dbs/db/colls/coll/"}],
}


def test_gate_is_off_without_backend():
    """A Python client does not attempt the Rust throughput-read path."""
    assert can_use_rust_backend_for_read_offer(backend=None, options={}, kwargs={}) is False


def test_gate_is_on_with_backend_and_no_kwargs():
    """A Rust-backed client with no extra kwargs routes its throughput read through Rust."""
    # The binding now exposes an offer entry point, so a Rust-backed client with no
    # extra kwargs routes its throughput read through Rust.
    assert can_use_rust_backend_for_read_offer(backend=object(), options={}, kwargs={}) is True


def test_gate_is_off_with_kwargs():
    """Extra kwargs keep the throughput read on Python until each knob is mirrored on Rust."""
    # Legacy forwards extra kwargs into QueryOffers; keep those on legacy until each
    # knob is mirrored on the Rust path.
    assert (
        can_use_rust_backend_for_read_offer(
            backend=object(), options={}, kwargs={"response_continuation_token_limit_in_kb": 8}
        )
        is False
    )


def test_gate_is_off_with_read_timeout():
    """A per-call socket timeout keeps the throughput read on Python."""
    assert (
        can_use_rust_backend_for_read_offer(
            backend=object(),
            options={Constants.Kwargs.READ_TIMEOUT: 5},
            kwargs={},
        )
        is False
    )


def test_gate_is_off_with_availability_strategy():
    """A per-call availability strategy keeps the throughput read on Python."""
    assert (
        can_use_rust_backend_for_read_offer(
            backend=object(),
            options={Constants.Kwargs.AVAILABILITY_STRATEGY: True},
            kwargs={},
        )
        is False
    )


def test_op_read_offer_mapped_to_binding_method():
    """``OP_READ_OFFER`` maps to the binding's ``read_offer`` method so a rename cannot silently unroute the operation."""
    # The op discriminator is mapped to the binding's `read_offer` function (the
    # async backend appends `_async` to reach `read_offer_async`).
    assert OP_READ_OFFER == "read_offer"
    assert OP_TO_BINDING_METHOD[OP_READ_OFFER] == "read_offer"


def test_builds_prepared_request_as_non_partitioned_query():
    """The Rust request queries the account-level offer with the required context."""
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
    """Rust receives the caller's timeout and excluded locations."""
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
    """Valid offer records keep the service response shape used by public methods."""
    offers = [{"id": "off-1", "offerType": "Invalid", "content": {"offerThroughput": 400}}]
    assert parse_read_offer_payload({"Offers": offers}) == offers


def test_parser_returns_empty_list_for_no_offers():
    """A resource with no offer produces an empty offer list."""
    assert parse_read_offer_payload({"Offers": []}) == []


def test_parser_rejects_missing_offers_field():
    """A missing offer list raises a clear parsing error."""
    with pytest.raises(ValueError):
        parse_read_offer_payload({})


def test_parser_rejects_non_list_offers():
    """An incorrectly shaped offer list raises a clear parsing error."""
    with pytest.raises(ValueError):
        parse_read_offer_payload({"Offers": {"id": "off-1"}})


def test_parser_rejects_non_object_offer_entry():
    """Each returned offer must be an object."""
    with pytest.raises(ValueError):
        parse_read_offer_payload({"Offers": ["not-an-object"]})


def _offer_read_connection():
    """Return a minimal client-connection stub suitable for offer-read tests."""
    return SimpleNamespace(
        default_headers={"x-ms-user-agent": "ua"},
        _query_compatibility_mode="Default",
        last_response_headers=None,
    )


def _patch_offer_read_headers(monkeypatch, captured, *, is_async=False):
    """Supply the headers that the request builder must preserve."""

    def _fake_get_headers(_client, headers, *_args):
        """Capture input headers and inject an intended-collection-rid for assertions."""
        captured["input_headers"] = dict(headers)
        result = dict(headers)
        result["x-ms-cosmos-intended-collection-rid"] = "rid-1"
        return result

    monkeypatch.setattr("azure.cosmos._offer_rust_routing.base.GetHeaders", _fake_get_headers)

    if is_async:
        async def _fake_set(_client, req_headers, _path, _request_params, _options):
            """Stand in for ``set_session_token_header_async``; injects a session token header."""
            req_headers["x-ms-session-token"] = "0:-1#1"

        monkeypatch.setattr(
            "azure.cosmos._offer_rust_routing.base.set_session_token_header_async", _fake_set
        )
    else:
        def _fake_set(_client, req_headers, _path, _request_params, _options):
            """Stand in for ``set_session_token_header``; injects a session token header."""
            req_headers["x-ms-session-token"] = "0:-1#1"

        monkeypatch.setattr(
            "azure.cosmos._offer_rust_routing.base.set_session_token_header", _fake_set
        )


def _assert_offer_read_prepared(prepared, captured):
    """Verify that a prepared offer-read request carries all required headers and fields."""
    assert prepared.op == OP_READ_OFFER
    # An empty partition key lets the service find the account-level offer.
    assert prepared.partition_key_header == "[]"
    assert prepared.headers["x-ms-cosmos-intended-collection-rid"] == "rid-1"
    assert prepared.headers["x-ms-session-token"] == "0:-1#1"
    assert prepared.headers[Constants.Kwargs.EXCLUDED_LOCATIONS] == ["West US"]
    assert prepared.headers[Constants.OVERALL_TIMEOUT_SECONDS] == 7
    assert (
        captured["input_headers"][http_constants.HttpHeaders.ContentType]
        == runtime_constants.MediaTypes.QueryJson
    )


def test_prepare_read_offer_request_carries_the_legacy_headers(monkeypatch):
    """The Rust request keeps headers prepared by the Python SDK."""
    captured = {}
    _patch_offer_read_headers(monkeypatch, captured)

    prepared = prepare_read_offer_request(
        client_connection=_offer_read_connection(),
        container_link="dbs/db/colls/coll/",
        offer_query=_OFFER_QUERY,
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 7,
        },
    )

    _assert_offer_read_prepared(prepared, captured)


@pytest.mark.asyncio
async def test_prepare_read_offer_request_async_carries_the_legacy_headers(monkeypatch):
    """The async request keeps the same required headers as the sync request."""
    captured = {}
    _patch_offer_read_headers(monkeypatch, captured, is_async=True)

    prepared = await prepare_read_offer_request_async(
        client_connection=_offer_read_connection(),
        container_link="dbs/db/colls/coll/",
        offer_query=_OFFER_QUERY,
        options={
            Constants.Kwargs.EXCLUDED_LOCATIONS: ["West US"],
            Constants.Kwargs.TIMEOUT: 7,
        },
    )

    _assert_offer_read_prepared(prepared, captured)


# ---------------------------------------------------------------------------
# Driver-owned headers must not ride along to the binding.
# ---------------------------------------------------------------------------
#
# The offer path is the one rust entry point that builds its request from a
# *complete legacy header map* (``_base.GetHeaders``) rather than from camelCase
# option-keys. That map necessarily contains the standard headers the rust driver
# writes for itself -- the authorization signature, the timestamp, the content
# type -- and forwarding them to the binding is wrong in a way nothing else
# catches: ``extract_op_modifiers`` has no translation arm for them, so it drops
# them silently, and under ``COSMOS_WIRE_STRICT`` it rejects the whole request.
#
# This was found by running the real throughput calls against a live account with
# COSMOS_WIRE_STRICT=1: ``get_throughput`` and ``replace_throughput`` failed on
# ``Cache-Control``, with ``Accept``, ``Content-Type`` and ``authorization``
# behind it. The query/feed path already stripped this exact set; the offer path
# never did.


def _prepared_offer_read_headers(monkeypatch, default_headers):
    """Build an offer-read PreparedRequest whose legacy headers are ``default_headers``."""

    def _fake_get_headers(_client, _headers, *_args):
        """Return a full legacy header map, the way ``_base.GetHeaders`` would."""
        return dict(default_headers)

    def _fake_set_session(_client, _req_headers, _path, _request_params, _options):
        """No-op stand-in for the session-token step."""

    monkeypatch.setattr("azure.cosmos._offer_rust_routing.base.GetHeaders", _fake_get_headers)
    monkeypatch.setattr(
        "azure.cosmos._offer_rust_routing.base.set_session_token_header", _fake_set_session
    )
    prepared = prepare_read_offer_request(
        client_connection=_offer_read_connection(),
        container_link="dbs/db/colls/coll",
        offer_query=_OFFER_QUERY,
        options={},
    )
    return prepared.headers


# The standard headers the rust driver builds itself, paired with a value the
# legacy path would really have produced for an offer query.
_DRIVER_OWNED_HEADER_SAMPLES = [
    ("Cache-Control", "no-cache"),
    ("Accept", "application/json"),
    ("Content-Type", "application/query+json"),
    ("authorization", "type%3dmaster%26ver%3d1.0%26sig%3dabc"),
    ("User-Agent", "azsdk-python-cosmos/4.0.0"),
    ("x-ms-date", "Sat, 09 Aug 2026 12:00:00 GMT"),
    ("x-ms-version", "2020-07-15"),
]


@pytest.mark.parametrize("header_name,header_value", _DRIVER_OWNED_HEADER_SAMPLES)
def test_offer_read_strips_driver_owned_header(monkeypatch, header_name, header_value):
    """Each header the driver writes itself is dropped before the binding sees it.

    Sending one is at best redundant and at worst a hard error under
    ``COSMOS_WIRE_STRICT``, which is the gate meant to catch genuine option
    divergence -- so a single stray header here disables that safety net.
    """
    headers = _prepared_offer_read_headers(
        monkeypatch,
        {header_name: header_value, "x-ms-activity-id": "act-1"},
    )
    assert header_name not in headers
    assert header_name.lower() not in {name.lower() for name in headers}
    # The header that is genuinely ours to send still survives the filter.
    assert headers["x-ms-activity-id"] == "act-1"


def test_offer_read_keeps_headers_the_driver_acts_on(monkeypatch):
    """Filtering removes only driver-owned names, never the request's real content.

    Guards against an over-broad filter: the ``x-ms-*`` headers below carry the
    session token, the consistency level and the intended-collection rid, and
    dropping any of them would change the request the service sees.
    """
    meaningful = {
        "x-ms-activity-id": "act-1",
        "x-ms-session-token": "0:-1#5",
        "x-ms-consistency-level": "Session",
        "x-ms-cosmos-intended-collection-rid": "rid-1",
        "x-ms-documentdb-query-iscontinuationexpected": "false",
    }
    headers = _prepared_offer_read_headers(
        monkeypatch, {**meaningful, "Cache-Control": "no-cache"},
    )
    for name, value in meaningful.items():
        assert headers[name] == value
    assert "Cache-Control" not in headers


def test_offer_read_sends_nothing_the_binding_cannot_translate(monkeypatch):
    """No key reaches the binding that ``extract_op_modifiers`` would reject.

    The end-to-end statement of the bug: with a realistic full legacy header map,
    every surviving key must either be one the binding translates or an ``x-ms-*``
    name it forwards. Anything else would be silently dropped in production and
    would fail the request outright under ``COSMOS_WIRE_STRICT``.
    """
    full_legacy_header_map = {
        "Cache-Control": "no-cache",
        "Accept": "application/json",
        "Content-Type": "application/query+json",
        "authorization": "type%3dmaster%26sig%3dabc",
        "User-Agent": "azsdk-python-cosmos/4.0.0",
        "x-ms-date": "Sat, 09 Aug 2026 12:00:00 GMT",
        "x-ms-version": "2020-07-15",
        "x-ms-activity-id": "act-1",
        "x-ms-session-token": "0:-1#5",
        "x-ms-consistency-level": "Session",
    }
    headers = _prepared_offer_read_headers(monkeypatch, full_legacy_header_map)
    untranslatable = [
        name for name in headers
        if not str(name).lower().startswith("x-ms-")
        and str(name) not in (Constants.Kwargs.EXCLUDED_LOCATIONS,
                              Constants.OVERALL_TIMEOUT_SECONDS)
    ]
    assert not untranslatable, (
        "These keys would reach the rust wire layer with no translation arm and be "
        f"silently dropped (or rejected under COSMOS_WIRE_STRICT): {untranslatable}"
    )
