# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for ``_backend.base.normalize_response_headers``.

``normalize_response_headers`` is a pure type-normalisation step at the
Rust backend boundary: the binding hands back a plain dict keyed by the
gateway's wire header names, and this function wraps it in a
``CaseInsensitiveDict`` so ``last_response_headers`` lookups are
case-insensitive and identical to the legacy core-python path (which
surfaces azure-core's ``CaseInsensitiveDict`` straight from
``copy.copy(response.headers)`` -- the raw gateway headers, unchanged).

It does **not** add, rename, or alias any header. In particular it does
not synthesise the un-prefixed double-``l`` LSN names (``x-ms-llsn`` /
``x-ms-item-llsn``): the gateway never emits those and the legacy SDK
never produced them, so inventing them on the rust path would create a
rust-only header surface. Both backends surface exactly the gateway's
names (``x-ms-cosmos-llsn``, ``x-ms-item-lsn``, ``lsn``, …).

These tests pin "pass everything through unchanged, invent nothing" so a
future regression that re-introduces an alias step shows up as a failure.
"""
from __future__ import annotations

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import normalize_response_headers


# --- Empty / None inputs -------------------------------------------------

def test_returns_none_for_none_input():
    """Prove a missing header collection remains absent."""
    assert normalize_response_headers(None) is None


def test_returns_none_for_empty_mapping():
    # An empty dict is treated the same as ``None`` so callers can keep
    # their existing ``if response.headers:`` guards unchanged.
    assert normalize_response_headers({}) is None


# --- Passthrough for unrelated headers ----------------------------------

def test_unrelated_headers_flow_through_unchanged():
    """Prove ordinary service headers retain their names and values."""
    headers = {
        "etag": '"abc"',
        "x-ms-request-charge": "5.71",
        "x-ms-session-token": "1:8#42=-1",
    }
    result = normalize_response_headers(headers)
    assert isinstance(result, CaseInsensitiveDict)
    assert result["etag"] == '"abc"'
    assert result["x-ms-request-charge"] == "5.71"
    assert result["x-ms-session-token"] == "1:8#42=-1"
    assert len(result) == 3


def test_result_is_case_insensitive():
    """Prove customers can read response headers with any letter case."""
    headers = {"ETag": '"abc"'}
    result = normalize_response_headers(headers)
    # Whatever case the caller wrote, lookups in any case must hit.
    assert result["etag"] == '"abc"'
    assert result["ETAG"] == '"abc"'


# --- LSN family: gateway names pass through, NO aliases invented --------

def test_lsn_family_passes_through_without_inventing_aliases():
    """The gateway's LSN header names flow through unchanged, and the
    function must NOT invent the un-prefixed double-``l`` aliases.

    The legacy core-python path surfaces only what the gateway emits
    (``x-ms-cosmos-llsn`` etc.). Synthesising ``x-ms-llsn`` /
    ``x-ms-item-llsn`` here would be a rust-only header surface the
    legacy SDK never produced -- exactly the behaviour that was removed.
    """
    headers = {
        "x-ms-cosmos-llsn": "42",
        "x-ms-cosmos-item-llsn": "41",
        "x-ms-cosmos-quorum-acked-llsn": "39",
        "x-ms-item-lsn": "42",
        "lsn": "42",
    }
    result = normalize_response_headers(headers)
    # Gateway names preserved exactly.
    assert result["x-ms-cosmos-llsn"] == "42"
    assert result["x-ms-cosmos-item-llsn"] == "41"
    assert result["x-ms-cosmos-quorum-acked-llsn"] == "39"
    assert result["x-ms-item-lsn"] == "42"
    assert result["lsn"] == "42"
    # No invented un-prefixed double-l aliases.
    assert "x-ms-llsn" not in result
    assert "x-ms-item-llsn" not in result
    assert "x-ms-quorum-acked-llsn" not in result
    # Same key count as the input -- nothing added.
    assert len(result) == 5

