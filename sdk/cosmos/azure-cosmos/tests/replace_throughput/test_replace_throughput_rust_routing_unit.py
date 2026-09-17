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
from azure.cosmos._backend.operations import OP_REPLACE_OFFER, OP_TO_BINDING_METHOD
from azure.cosmos._helpers._request_offer import build_replace_offer_request
from azure.cosmos._offer_rust_routing import can_use_rust_backend_for_replace_throughput, build_replace_offer_from_connection

_OFFER = {"id": "offer", "_self": "offers/AAAAAA==/", "content": {"offerThroughput": 500}}


@pytest.mark.parametrize(
    "backend,options,kwargs,expected",
    [
        (LEGACY_BACKEND, {}, {}, False),
        (SimpleNamespace(name="rust"), {}, {}, True),
        (SimpleNamespace(name="rust"), {}, {"unknown": 1}, False),
        (SimpleNamespace(name="rust"), {"read_timeout": 5}, {}, False),
        (SimpleNamespace(name="rust"), {"availabilityStrategy": True}, {}, False),
        (SimpleNamespace(name="rust"), {"initialHeaders": {"USER-AGENT": "custom"}}, {}, False),
    ],
)
def test_replace_gate(backend, options, kwargs, expected):
    assert can_use_rust_backend_for_replace_throughput(backend=backend, options=options, kwargs=kwargs) is expected


@pytest.mark.parametrize("resource_link", ["dbs/db", "dbs/db/colls/coll"])
def test_replace_preparation_never_uses_legacy_transport(monkeypatch, resource_link):
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
    prepared = build_replace_offer_from_connection(**kwargs)
    forbidden.assert_not_called()
    assert (_OFFER, options) == original
    assert prepared.op == OP_REPLACE_OFFER == OP_TO_BINDING_METHOD[OP_REPLACE_OFFER]
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


def test_replace_builder_requires_offer_identity():
    with pytest.raises(KeyError, match="_self"):
        build_replace_offer_request(
            resource_link="dbs/db",
            offer_body={"content": {}},
            request_options={},
            default_headers={},
        )
