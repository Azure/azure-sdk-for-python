# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original create-only vectors from composite CRUD/encoding/validation tests."""

import json

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.http_constants import SubStatusCodes

INVALID_IDS = [
    pytest.param("ID_with_back/slash", id="slash"),
    pytest.param("ID_\\with_forward_slashes", id="backslash"),
    pytest.param("ID_with_question?_mark", id="question"),
    pytest.param("ID_with_#pound", id="pound"),
    pytest.param("ID_with_tab\t", id="tab"),
    pytest.param("ID\r_with_return_carriage", id="carriage-return"),
    pytest.param("ID_with_newline\n", id="trailing-newline"),
    pytest.param("ID_with_newline\n2", id="embedded-newline"),
    pytest.param("ID_with_more_than_255" + "_add" * 255, id="oversize-sync"),
    pytest.param("ID_with_more_than_255" + "_added" * 255, id="oversize-async"),
    pytest.param("ID_with_trailing_spaces   ", id="trailing-spaces"),
]

INCOMPLETE_KEYS = [
    pytest.param(
        PartitionKey(path=["/address/state/city", "/address/city/state"], kind="MultiHash"),
        {"id": "document1", "address": {
            "street": "1 Microsoft Way", "city": "Redmond", "state": "WA", "zip code": 98052,
        }},
        id="missing-nested-components",
    ),
    pytest.param(
        PartitionKey(path=["/city", "/zipcode"], kind="MultiHash"),
        {"id": "document3", "key": "value3", "city": "Vancouver"},
        id="missing-second-component",
    ),
]

EMOJI_CASES = [
    pytest.param(False, "celebration \U0001f389\U0001f38a \u2014 caf\u00e9 \u65e5\u672c \U0001f30d", id="point-read"),
    pytest.param(True, "query \U0001f389 \u2014 caf\u00e9 \u65e5\u672c", id="query"),
]
COMPACT_CONTENT = "create caf\u00e9 \u65e5\u672c \U0001f389"
AAD_CONTENT = "\u65e5\u672c\U0001f389"
MEBIBYTE = 1024 * 1024


def assert_bad_hierarchical_key(error, native):
    assert error.status_code == 400
    assert error.sub_status == SubStatusCodes.PARTITION_KEY_MISMATCH
    if native is not None:
        native.assert_called_once()


def assert_native_body(native, body, *, compact):
    """Observe prepared bytes; binding transport tests separately pin no re-encoding."""
    if native is None:
        return
    native.assert_called_once()
    prepared = native.call_args.args[1]
    assert isinstance(prepared.body_bytes, bytes)
    assert json.loads(prepared.body_bytes) == body
    expected = json.dumps(body, separators=(",", ":"), ensure_ascii=not compact).encode("utf-8")
    assert prepared.body_bytes == expected


def large_cjk_body():
    return {"id": "large-cjk", "pk": "pk", "content": "\u65e5" * 400000}


def assert_stored_sequence(stored, original, generated, explicit):
    assert len(stored) == 3, "The suppressed create must also persist exactly one item"
    ids = {item["id"] for item in stored}
    assert len(ids) == 3
    assert generated["id"] in ids and explicit["id"] in ids
    assert generated["id"] != explicit["id"]
    for item in stored:
        for key, value in original.items():
            assert item[key] == value
