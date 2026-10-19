# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Direct offer replacement preserves identity, body and caller controls."""

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
from azure.cosmos._backend.operations import OP_REPLACE_THROUGHPUT, OP_TO_BINDING_FUNCTION_NAME
from azure.cosmos._helpers._request_throughput import build_replace_throughput_request
from azure.cosmos._throughput_rust_routing import can_use_rust_backend_for_replace_throughput, build_replace_throughput_from_connection

_OFFER = {"id": "offer", "_self": "offers/AAAAAA==/", "content": {"offerThroughput": 500}}


@pytest.mark.parametrize(
    "backend,options,kwargs,expected",
    [
        (LEGACY_BACKEND, {}, {}, False),
        (SimpleNamespace(name="rust"), {}, {}, True),
        (SimpleNamespace(name="rust"), {}, {"unknown": 1}, False),
        (SimpleNamespace(name="rust"), {"availabilityStrategy": True}, {}, False),
        (SimpleNamespace(name="rust"), {"initialHeaders": {"USER-AGENT": "custom"}}, {}, False),
    ],
)
def test_replace_gate_rust(backend, options, kwargs, expected):
    """Only a plain throughput replacement on the Rust backend is eligible.

    Unsupported Rust inputs are rejected by the workflow policy, not routed
    to legacy. Explicit legacy selection is reserved for comparison runs.
    """
    assert can_use_rust_backend_for_replace_throughput(backend=backend, options=options, kwargs=kwargs) is expected


@pytest.mark.parametrize("resource_link", ["dbs/db", "dbs/db/colls/coll"])
def test_replace_preparation_never_uses_legacy_transport_rust(monkeypatch, resource_link):
    """Building a throughput replacement touches no legacy code and keeps the offer's identity.

    The same five legacy helpers are replaced with mocks that fail if called,
    and the inputs are compared against a copy afterwards so an in-place edit
    of the caller's offer or options would be caught.

    The identity check is what separates this from the read case. The offer's
    resource id is pulled out of its ``_self`` link and becomes the item id on
    the request. Get that wrong and the call rewrites the throughput of a
    different resource, which no later assertion would notice.

    The body is the whole offer, unchanged. The access condition turns into an
    ``if-match`` header carrying the etag, which is what stops a replacement
    overwriting a change someone else made in between. The caller's activity id
    and session token pass through, while the default authorization header is
    dropped, and the timeout and excluded locations move into the settings
    rather than becoming headers.

    Both a database link and a container link are covered, and neither is
    rewritten. The partition key is an empty list, since an offer has none.
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
    options = {
        "containerRID": "owner-rid",
        "excludedLocations": ["West US"],
        "timeout": 12,
        "accessCondition": {"type": "IfMatch", "condition": '"etag"'},
        "initialHeaders": {"X-MS-ACTIVITY-ID": "caller", "X-MS-SESSION-TOKEN": "raw-session"},
    }
    original = deepcopy((_OFFER, options))
    kwargs = dict(
        client_connection=SimpleNamespace(default_headers={"Authorization": "SDK default"}),
        container_link=resource_link,
        offer=_OFFER,
        options=options,
    )
    prepared = build_replace_throughput_from_connection(**kwargs)
    forbidden.assert_not_called()
    assert (_OFFER, options) == original
    assert prepared.op == OP_REPLACE_THROUGHPUT == OP_TO_BINDING_FUNCTION_NAME[OP_REPLACE_THROUGHPUT]
    assert prepared.container_link == resource_link
    assert legacy_partition_key_from_request(prepared) == "[]"
    assert prepared.item_id == "AAAAAA=="
    assert json.loads(prepared.body_bytes) == _OFFER
    assert wire_headers(prepared) == {
        "x-ms-cosmos-intended-collection-rid": "owner-rid",
        "x-ms-activity-id": "caller",
        "x-ms-session-token": "raw-session",
        "if-match": '"etag"',
    }
    assert settings_options(prepared) == {"excludedLocations": ["West US"], "timeout_seconds": 12}


def test_replace_builder_requires_offer_identity_rust():
    """An offer with no ``_self`` link is refused rather than sent without a target.

    The resource id lives in that link and is the only thing saying which offer
    is being replaced. Without it the builder raises a ``KeyError`` naming
    ``_self``.

    Failing here is the safe outcome: a request built without a target is
    either rejected later with a far less obvious error, or worse, applied
    somewhere unintended.
    """
    with pytest.raises(KeyError, match="_self"):
        build_replace_throughput_request(
            resource_link="dbs/db",
            offer_body={"content": {}},
            request_options={},
            default_headers={},
        )


@pytest.mark.parametrize("asynchronous", [False, True])
def test_native_replacement_accepts_deadline_and_attempt_controls_rust(asynchronous):
    from azure.cosmos import _rust

    prepared = build_replace_throughput_request(
        resource_link="dbs/db",
        offer_body=_OFFER,
        request_options={},
        default_headers={},
    )
    function = _rust.replace_throughput_async if asynchronous else _rust.replace_throughput
    # An invalid budget must fail before even resolving the driver handle.
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        function("unused-driver", prepared, timeout_seconds=0, include_attempts=True)
    assert not hasattr(_rust, "read_offer")
    assert not hasattr(_rust, "replace_offer")
