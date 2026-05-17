# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for ``_backend.base.normalize_response_headers``.

The Rust binding emits a handful of LSN-family response headers under
their ``cosmos-``-prefixed wire names (``x-ms-cosmos-llsn`` and friends);
the legacy core-python path historically surfaced the same data under
the un-prefixed legacy names (``x-ms-llsn`` etc.). At the Rust backend
boundary, ``normalize_response_headers`` *aliases* each prefixed key
into its legacy spelling — both keys end up in the resulting
``CaseInsensitiveDict`` with the same value — so customer code reading
``last_response_headers["x-ms-llsn"]`` works the same on both backends
and the parity diff can presence-check a single canonical key. The
prefixed form is preserved so anything that reads it directly keeps
working.

These tests pin that contract so a future change to the alias map (or
to its merge semantics — e.g. flipping back to a destructive rename, or
letting the alias clobber an existing legacy value) shows up as a test
failure rather than as a silent parity drift.
"""
from __future__ import annotations

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.base import (
    _RUST_PREFIXED_TO_LEGACY_ALIASES,
    normalize_response_headers,
)


# --- Empty / None inputs -------------------------------------------------

def test_returns_none_for_none_input():
    assert normalize_response_headers(None) is None


def test_returns_none_for_empty_mapping():
    # An empty dict is treated the same as ``None`` so callers can keep
    # their existing ``if response.headers:`` guards unchanged.
    assert normalize_response_headers({}) is None


# --- Passthrough for unrelated headers ----------------------------------

def test_unrelated_headers_flow_through_unchanged():
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
    headers = {"ETag": '"abc"'}
    result = normalize_response_headers(headers)
    # Whatever case the caller wrote, lookups in any case must hit.
    assert result["etag"] == '"abc"'
    assert result["ETAG"] == '"abc"'


# --- LSN-family alias ----------------------------------------------------

def test_lsn_family_prefixed_names_gain_legacy_aliases():
    headers = {
        "x-ms-cosmos-llsn": "42",
        "x-ms-cosmos-item-llsn": "41",
        "x-ms-cosmos-quorum-acked-lsn": "40",
        "x-ms-cosmos-quorum-acked-llsn": "39",
    }
    result = normalize_response_headers(headers)
    # Prefixed spellings are preserved (the binding emits them; the
    # parity harness and any forward-compatible reader may still want
    # them)...
    assert result["x-ms-cosmos-llsn"] == "42"
    assert result["x-ms-cosmos-item-llsn"] == "41"
    assert result["x-ms-cosmos-quorum-acked-lsn"] == "40"
    assert result["x-ms-cosmos-quorum-acked-llsn"] == "39"
    # ...and the legacy un-prefixed names are added as aliases with the
    # same values, so legacy customer code reading either spelling works.
    assert result["x-ms-llsn"] == "42"
    assert result["x-ms-item-llsn"] == "41"
    assert result["x-ms-quorum-acked-lsn"] == "40"
    assert result["x-ms-quorum-acked-llsn"] == "39"
    # 4 prefixed + 4 alias entries.
    assert len(result) == 8


def test_alias_lookup_is_case_insensitive_on_input():
    # ``CaseInsensitiveDict`` makes the prefixed-key lookup case-blind,
    # so any casing the binding might hand us still produces the alias.
    headers = {"X-MS-Cosmos-Llsn": "42"}
    result = normalize_response_headers(headers)
    assert result["x-ms-llsn"] == "42"
    # Original key is preserved (case-insensitive lookup still hits).
    assert result["X-MS-Cosmos-Llsn"] == "42"
    assert result["x-ms-cosmos-llsn"] == "42"


# --- Collision dedupe ----------------------------------------------------

def test_existing_legacy_name_is_not_overwritten():
    # If the driver ever started surfacing the un-prefixed form on its
    # own (so we get *both* spellings on the way in), the value already
    # under the legacy spelling wins — the alias step must not clobber
    # it with the prefixed value.
    headers = {
        "x-ms-llsn": "100",            # canonical, already set
        "x-ms-cosmos-llsn": "999",     # would otherwise be aliased in
    }
    result = normalize_response_headers(headers)
    assert result["x-ms-llsn"] == "100"
    # Prefixed form is still preserved with its own value; only the
    # *alias add* is skipped because the legacy key already existed.
    assert result["x-ms-cosmos-llsn"] == "999"
    assert len(result) == 2


# --- Alias map auditability ---------------------------------------------

def test_alias_map_is_lowercase_only():
    # The runtime lookup compares keys via ``CaseInsensitiveDict``, but
    # keeping the map keys lowercase is the convention and matches the
    # wire spelling. A mixed-case key here would still work but would be
    # a maintenance smell.
    for key in _RUST_PREFIXED_TO_LEGACY_ALIASES:
        assert key == key.lower(), (
            "alias map key {!r} must be all-lowercase".format(key)
        )


def test_alias_map_never_aliases_to_itself():
    # A no-op entry would clutter the table and confuse future readers
    # about whether an alias is intentional.
    for src, dst in _RUST_PREFIXED_TO_LEGACY_ALIASES.items():
        assert src != dst, "alias {!r} -> {!r} is a no-op".format(src, dst)

