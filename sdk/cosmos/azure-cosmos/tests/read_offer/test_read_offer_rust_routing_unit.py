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
from azure.cosmos._backend.operations import OP_READ_OFFER, OP_TO_BINDING_FUNCTION_NAME
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
    """Only a plain offer read on the Rust backend is eligible for the Rust path.

    Five cases: the legacy backend is never eligible; a bare Rust call is; and
    an unknown keyword, a ``read_timeout`` or an availability strategy each
    send the call back to legacy.

    The gate has to refuse anything it cannot honour exactly. Reading throughput
    while quietly ignoring a timeout the caller asked for would be worse than
    not taking the fast path at all.
    """
    assert can_use_rust_backend_for_read_offer(backend=backend, options=options, kwargs=kwargs) is expected


@pytest.mark.parametrize("header", sorted(HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE))
def test_offer_read_refuses_customer_overrides(header):
    """Supplying any header the driver would overwrite sends the call to legacy.

    Runs once per header in that set. If a customer sets one of them by hand,
    the Rust path is refused rather than silently replacing their value.

    Each header is supplied in upper case while the set is stored in lower
    case, so this also pins that the check ignores capitalisation. Header names
    are case insensitive on the wire, and a case-sensitive comparison here
    would let the override through unnoticed.
    """
    assert not can_use_rust_backend_for_read_offer(
        backend=RUST_BACKEND,
        options={"initialHeaders": {header.upper(): "custom"}},
        kwargs={},
    )


def test_header_policies_remain_distinct():
    """The two header lists mean different things and must not blur together.

    One list is headers the driver would silently overwrite: ``accept``,
    ``cache-control``, ``user-agent`` and ``x-ms-version``. A caller setting
    these gets the call sent to legacy so their value is honoured.

    The other is headers the driver regenerates for itself. The part unique to
    it -- ``authorization``, ``content-type`` and ``x-ms-date`` -- is
    machinery no caller should be setting, so regenerating them is fine.

    Finally, activity id and session token must appear in neither list. Those
    carry caller meaning and have to pass through untouched.

    Memberships are pinned literally because moving a header between these
    lists silently changes whether customer values survive.
    """
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
    """Building an offer read touches no legacy code and resolves every header conflict correctly.

    Five legacy helpers -- header building, session token handling, the
    authorization header and guid generation -- are replaced with mocks that
    fail if called. Running the legacy preparation as well would mean signing
    and tagging every request twice.

    The inputs are compared against a copy afterwards, because a builder that
    edits the caller's options dict in place would corrupt a dict the caller
    may reuse.

    Header precedence is the substance here, and three sources disagree on
    purpose. The throughput bucket is 1 in the defaults, 2 in the caller's
    initial headers and 3 in the options; the options win. The activity id is
    set in both defaults and initial headers; the caller's wins. Everything the
    driver regenerates is seeded with "SDK default" and must be dropped
    entirely. An unrecognised ``X-Custom`` must survive.

    The session token is the subtle one: the raw header passes through, while
    the ``sessionToken`` option is ignored, because offers are master resources
    and session tokens do not apply to them.

    The link is checked with and without surrounding slashes, and the partition
    key comes out as an empty list, since an offer has no partition key.
    """
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
    assert prepared.op == OP_READ_OFFER == OP_TO_BINDING_FUNCTION_NAME[OP_READ_OFFER]
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


def test_offer_builder_does_not_generate_activity_or_session_headers():
    """With nothing supplied, the builder generates no headers of its own.

    No options and no default headers must produce an empty header set. In
    particular the builder does not invent an activity id or a session token.

    Those belong to the layer that actually sends the request, and generating
    them here would mean every prepared request carried an id that never
    matched the one the service saw.
    """
    prepared = build_read_offer_request(
        resource_link="dbs/db",
        offer_query=_OFFER_QUERY,
        request_options={},
        default_headers={},
    )
    assert wire_headers(prepared) == {}


@pytest.mark.parametrize("initial_headers", [[], False, "header"])
def test_offer_builder_rejects_invalid_initial_headers(initial_headers):
    """Initial headers that are not a mapping are refused by name.

    An empty list, ``False`` and a bare string are each rejected with a
    ``TypeError`` saying a mapping was expected.

    All three would otherwise fail somewhere further along, and the string is
    the nastiest: it is iterable, so a loose implementation could iterate it
    character by character and build nonsense headers instead of complaining.
    """
    with pytest.raises(TypeError, match="initial_headers must be a mapping"):
        build_read_offer_request(
            resource_link="dbs/db", offer_query=_OFFER_QUERY,
            request_options={"initialHeaders": initial_headers}, default_headers={},
        )


@pytest.mark.parametrize("payload", [{}, {"Offers": {}}, {"Offers": ["invalid"]}])
def test_offer_parser_rejects_malformed_payload(payload):
    """A payload without a usable list of offers is rejected, not guessed at.

    Three shapes: no ``Offers`` key at all, ``Offers`` holding a dict instead
    of a list, and a list holding something that is not an offer.

    Each raises a ``ValueError`` naming the read_offer payload. Throughput
    numbers come from here, so a parser that returns empty or partial results
    for a malformed response would report the wrong throughput rather than
    admit it could not read the answer.
    """
    with pytest.raises(ValueError, match="read_offer Rust payload"):
        parse_read_offer_payload(payload)


@pytest.mark.parametrize("offers", [[], [{"id": "offer", "content": {"offerThroughput": 400}}]])
def test_offer_parser_preserves_records(offers):
    """Valid offer records come back exactly as they arrived.

    Both an empty list and a single offer carrying a throughput value pass
    through unchanged. The parser's job is to validate the envelope, not to
    reshape, filter or normalise the records inside it.

    The empty list matters separately: no offers is a legitimate answer and
    must not be treated as a malformed payload.
    """
    assert parse_read_offer_payload({"Offers": offers}) == offers


def test_offer_headers_belong_to_response_not_later_client_diagnostics():
    from types import SimpleNamespace
    from azure.cosmos._backend.contracts import BackendResponse
    from azure.cosmos._offer_rust_routing import process_read_offer_response, offer_response_headers

    connection = SimpleNamespace(last_response_headers={})
    result = process_read_offer_response(
        BackendResponse(status_code=200, headers={"etag": "offer-response"}, body=b'{"Offers":[]}'),
        client_connection=connection,
    )
    connection.last_response_headers = {"etag": "another-operation"}
    headers = offer_response_headers(result, connection)
    assert headers["etag"] == "offer-response"
    headers.clear()
    assert result.get_response_headers()["etag"] == "offer-response"
    assert connection.last_response_headers["etag"] == "another-operation"


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("replace_offer", [False, True])
def test_native_offer_entries_accept_direct_requests_before_io(monkeypatch, is_async, replace_offer):
    """The real Rust entry points accept a prepared offer request without any account.

    Covers read and replace, sync and async, against the actual compiled
    module with strict request parsing switched on.

    Each call is expected to fail with "no driver registered for handle". That
    specific failure is the result being checked: the request was fully parsed
    and accepted before the driver handle was looked up, which means the
    prepared shape really does satisfy the Rust side.

    Checking it this way needs no driver and no network, so a mismatch between
    what Python builds and what Rust expects is caught here rather than in a
    live test.
    """
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
