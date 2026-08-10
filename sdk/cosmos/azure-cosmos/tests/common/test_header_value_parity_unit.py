# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Differential test for header *values* across the two backends -- no network.

``test_rust_option_key_parity`` proves the two engines agree on which option
*keys* exist. It cannot prove they agree on the header each key produces or on
the value written into it, because it only compares key sets.

This module closes that half. For one options dict it computes the wire headers
*both* engines would emit and asserts they are identical:

* **legacy** -- call ``_base.GetHeaders`` directly, then subtract the headers it
  stamps on every request regardless of options (auth, date, activity-id, ...)
  so only the option-derived ones remain.
* **rust** -- call ``flatten_options_to_headers`` (the Python half of the split
  mapping), then apply the camelCase -> ``x-ms-*`` table parsed straight out of
  ``extract_op_modifiers`` in ``azure_cosmos_rust/src/wire/request.rs`` (the Rust half).

Reading the table from the Rust source rather than restating it here is the
whole point: a hand-written copy would drift silently, which is the exact class
of bug this is meant to catch.

This is what makes the "byte for byte" promise in ``_request_headers`` a tested
claim instead of a comment. It catches a wrong wire name, a dropped truthy gate
(``indexing_directive=Default`` is ``0`` and must ship *no* header), and a value
formatted differently by the two paths (a list of trigger ids must comma-join to
``"t1,t2"``, not arrive as a Python list repr).

Needs no built extension and no emulator -- just the two source files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Mapping

import pytest

from azure.cosmos import _base
from azure.cosmos._helpers._request_headers import (
    RUST_HANDLED_OPTION_KEYS,
    flatten_options_to_headers,
)

# wire/request.rs lives at <pkg-root>/azure_cosmos_rust/src/wire/request.rs; this file is at
# <pkg-root>/tests/common/, so two parents up from the test dir is the pkg root.
_WIRE_RS = (
    Path(__file__).resolve().parents[2] / "azure_cosmos_rust" / "src" / "wire" / "request.rs"
)

# Headers whose value is regenerated per call, so they can never compare equal
# across two invocations. They are not option-derived, so dropping them costs no
# coverage: ``x-ms-activity-id`` is a fresh guid per request and ``x-ms-date`` is
# the current time.
_PER_CALL_NONDETERMINISTIC = frozenset({"x-ms-activity-id", "x-ms-date"})


# Option-keys deliberately outside the generic diff because the two engines
# represent them in structurally different places, not because they are
# untested. Comparing them as headers would fail for the wrong reason.
#
#   * ``sessionToken`` -- legacy emits it from ``_base.set_session_token_header``
#     (which consults the session container and the request's consistency
#     level), not from ``GetHeaders``, so ``GetHeaders`` produces nothing to diff.
#   * ``responsePayloadOnWriteDisabled`` -- legacy turns it into ``Prefer:
#     return=minimal`` and only for non-GET ``docs`` requests; the binding lifts
#     it to the driver's typed ContentResponseOnWrite field. Covered on its own
#     below by :func:`test_no_response_on_write_maps_to_prefer_on_legacy`.
#   * ``excludedLocations`` / ``availabilityStrategy`` -- routing and hedging
#     controls lifted to typed driver fields; they are not wire headers on
#     either path (``availabilityStrategy`` appears nowhere in ``_base``).
#   * ``initialHeaders`` -- the customer's own headers, forwarded verbatim as a
#     nested map rather than translated through the option table.
_STRUCTURALLY_EXCLUDED_KEYS = frozenset({
    "sessionToken",
    "responsePayloadOnWriteDisabled",
    "excludedLocations",
    "availabilityStrategy",
    "initialHeaders",
})


def _extract_op_modifiers_body() -> str:
    """Return just the body of ``fn extract_op_modifiers`` from wire/request.rs.

    Scoping the parse to that one function keeps unrelated string literals
    elsewhere in the file out of the mapping table.
    """
    src = _WIRE_RS.read_text(encoding="utf-8")
    start = src.find("fn extract_op_modifiers")
    assert start != -1, f"could not find extract_op_modifiers in {_WIRE_RS}"
    end = src.find("\nfn ", start + 1)
    return src[start:end if end != -1 else len(src)]


def _rust_option_key_to_wire_name() -> Dict[str, str]:
    """Parse the lower-cased option-key -> wire-header-name table out of Rust.

    Two arm shapes carry a mapping::

        "maxitemcount" => Some("x-ms-max-item-count"),        # single line
        "offerenableruperminutethroughput" => {               # wrapped for width
            Some("x-ms-offer-is-ru-per-minute-throughput-enabled")
        }

    Both are collected. Arms that map to ``None`` (the ``x-ms-*`` / ``prefer``
    passthrough) carry no rename and are absent from the result, which is
    correct: the caller falls back to the key itself for those.
    """
    body = _extract_op_modifiers_body()
    mapping = dict(re.findall(r'"([^"]+)"\s*=>\s*Some\("([^"]+)"\)', body))
    for key, arm_body in re.findall(r'"([^"]+)"\s*=>\s*\{(.*?)\n\s*\}', body, re.S):
        wire_name = re.search(r'Some\("([^"]+)"\)', arm_body)
        if wire_name:
            mapping.setdefault(key, wire_name.group(1))
    return mapping


class _StubConnectionPolicy:
    """The one connection-policy field ``GetHeaders`` reads."""

    ResponsePayloadOnWriteDisabled = False


class _StubClientConnection:
    """Minimal stand-in for the client connection ``GetHeaders`` expects.

    ``master_key`` / ``resource_tokens`` are left unset so ``GetHeaders`` skips
    the authorization step -- signing needs a real key and would add a header
    that is not option-derived anyway.
    """

    UseMultipleWriteLocations = False
    master_key = None
    resource_tokens = None
    client_id = None

    def __init__(self):
        self.connection_policy = _StubConnectionPolicy()


def _legacy_option_headers(
    options: Mapping[str, Any],
    *,
    resource_type: str = "docs",
    verb: str = "get",
) -> Dict[str, Any]:
    """Return only the headers ``GetHeaders`` emits *because of* ``options``.

    Computed by differencing against the same call with an empty options dict,
    so every unconditional header (accept, sdk-capabilities, thin-client
    routing, ...) cancels out and what remains is attributable to an option.
    """
    connection = _StubClientConnection()
    common = dict(
        verb=verb, path="/dbs/d/colls/c", resource_id="RID==",
        resource_type=resource_type, operation_type="Read",
    )
    with_options = _base.GetHeaders(connection, {}, options=options, **common)
    without_options = _base.GetHeaders(connection, {}, options={}, **common)
    baseline = {name.lower(): value for name, value in without_options.items()}
    return {
        name.lower(): value
        for name, value in with_options.items()
        if name.lower() not in _PER_CALL_NONDETERMINISTIC
        and baseline.get(name.lower()) != value
    }


def _rust_option_headers(options: Mapping[str, Any]) -> Dict[str, Any]:
    """Return the wire headers the rust path would send for ``options``.

    Applies both halves of the split mapping: the Python prep, then the Rust
    rename table. A key with no rename arm reaches the wire under its own
    (lower-cased) name, mirroring ``HeaderName::from(lower)`` in the binding.
    """
    rename = _rust_option_key_to_wire_name()
    return {
        rename.get(key.lower(), key.lower()): value
        for key, value in flatten_options_to_headers(options).items()
    }


def _assert_header_parity(options: Mapping[str, Any], *, resource_type: str = "docs") -> None:
    """Assert both engines emit the same option-derived headers for ``options``.

    Values are compared as strings because that is what reaches the socket on
    both paths: legacy hands native Python objects to azure-core and the binding
    stringifies with ``str()``, so ``100`` and ``"100"`` are the same wire bytes.
    """
    legacy = _legacy_option_headers(options, resource_type=resource_type)
    rust = _rust_option_headers(options)
    legacy_wire = {name: str(value) for name, value in legacy.items()}
    rust_wire = {name: str(value) for name, value in rust.items()}
    assert legacy_wire == rust_wire, (
        "The two engines disagree on the wire headers for options={!r}.\n"
        "  legacy (_base.GetHeaders): {}\n"
        "  rust   (flatten_options_to_headers + extract_op_modifiers): {}\n"
        "Fix the Python prep (azure/cosmos/_helpers/_request_headers.py) and/or the "
        "Rust table (azure_cosmos_rust/src/wire/request.rs) so both emit the same bytes."
    ).format(dict(options), legacy_wire, rust_wire)


# ---------------------------------------------------------------------------
# Per-option parity: a representative truthy value for every mapped key.
# ---------------------------------------------------------------------------

# Each entry is one option-key with a value a customer could realistically pass.
# ``id`` is the key name so a failure names the offending knob directly.
_TRUTHY_CASES = [
    ("preTriggerInclude", ["t1", "t2"]),
    ("preTriggerInclude", "t1"),
    ("postTriggerInclude", ["p1", "p2"]),
    ("postTriggerInclude", "p1"),
    ("indexingDirective", "Include"),
    ("maxItemCount", 100),
    ("priorityLevel", "High"),
    ("throughputBucket", 2),
    ("containerRID", "RID=="),
    ("maxIntegratedCacheStaleness", 5000),
    ("offerThroughput", 400),
    ("autoUpgradePolicy", '{"maxThroughput":4000}'),
    ("continuation", "token-1"),
    ("contentType", "application/query+json"),
    ("correlatedActivityId", "corr-1"),
    ("disableRUPerMinuteUsage", True),
    ("enableCrossPartitionQuery", True),
    ("enableScanInQuery", True),
    ("enableScriptLogging", True),
    ("isQueryPlanRequest", True),
    ("offerEnableRUPerMinuteThroughput", True),
    ("offerType", "S1"),
    ("populateIndexMetrics", True),
    ("populatePartitionKeyRangeStatistics", True),
    ("populateQueryAdvice", True),
    ("populateQueryMetrics", True),
    ("populateQuotaInfo", True),
    ("queryVersion", "1.0"),
    ("resourceTokenExpirySeconds", 60),
    ("responseContinuationTokenLimitInKb", 8),
    ("supportedQueryFeatures", "OrderBy"),
    ("consistencyLevel", "Eventual"),
]


@pytest.mark.parametrize(
    "option_key,option_value", _TRUTHY_CASES,
    ids=[f"{key}-{index}" for index, (key, _) in enumerate(_TRUTHY_CASES)],
)
def test_truthy_option_produces_identical_header_on_both_engines(option_key, option_value):
    """A set option lands on the same header with the same value on both paths.

    This is the check that catches a wrong wire name in the Rust table (say
    ``x-ms-max-items`` instead of ``x-ms-max-item-count``) and a value the two
    paths format differently -- notably a list of trigger ids, which legacy
    comma-joins and the binding would otherwise stringify as a Python list.
    """
    _assert_header_parity({option_key: option_value})


# ---------------------------------------------------------------------------
# Falsy parity: the truthy gate is where the two paths are easiest to drift.
# ---------------------------------------------------------------------------

# ``GetHeaders`` gates most options behind ``if options.get(key):``, so a falsy
# value must emit NO header at all. The rust prep has to reproduce each gate by
# hand, which is exactly the kind of thing that gets missed when a knob is added.
# The customer-visible cases: ``indexing_directive=IndexingDirective.Default``
# is ``0`` and ``throughput_bucket=0`` is not a real bucket -- both must ship
# nothing rather than a header carrying ``"0"``.
_FALSY_CASES = [
    ("indexingDirective", 0),
    ("throughputBucket", 0),
    ("maxItemCount", 0),
    ("maxIntegratedCacheStaleness", 0),
    ("offerThroughput", 0),
    ("responseContinuationTokenLimitInKb", 0),
    ("resourceTokenExpirySeconds", 0),
    ("consistencyLevel", ""),
    ("continuation", ""),
    ("priorityLevel", ""),
    ("contentType", ""),
    ("correlatedActivityId", ""),
    ("queryVersion", ""),
    ("supportedQueryFeatures", ""),
    ("offerType", ""),
    ("autoUpgradePolicy", ""),
    ("containerRID", ""),
    ("preTriggerInclude", []),
    ("postTriggerInclude", []),
    ("disableRUPerMinuteUsage", False),
    ("enableCrossPartitionQuery", False),
    ("enableScanInQuery", False),
    ("enableScriptLogging", False),
    ("isQueryPlanRequest", False),
    ("offerEnableRUPerMinuteThroughput", False),
    ("populateIndexMetrics", False),
    ("populatePartitionKeyRangeStatistics", False),
    ("populateQueryAdvice", False),
    ("populateQueryMetrics", False),
    ("populateQuotaInfo", False),
]


@pytest.mark.parametrize(
    "option_key,option_value", _FALSY_CASES,
    ids=[f"{key}-{index}" for index, (key, _) in enumerate(_FALSY_CASES)],
)
def test_falsy_option_emits_no_header_on_either_engine(option_key, option_value):
    """A falsy option ships no header on either path.

    Asserted twice over: the two engines must agree with each other, and both
    must emit nothing at all -- so this still fails if a future change makes
    *both* paths start sending ``"0"``.
    """
    _assert_header_parity({option_key: option_value})
    assert not _legacy_option_headers({option_key: option_value}), (
        f"legacy unexpectedly emitted a header for falsy {option_key}={option_value!r}"
    )
    assert not _rust_option_headers({option_key: option_value}), (
        f"the rust prep unexpectedly emitted a header for falsy "
        f"{option_key}={option_value!r}"
    )


# ---------------------------------------------------------------------------
# accessCondition, combinations, and the structurally-different keys.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "condition_type,expected_header",
    [("IfMatch", "if-match"), ("IfNoneMatch", "if-none-match")],
)
def test_access_condition_becomes_the_same_conditional_header(condition_type, expected_header):
    """``etag`` / ``match_condition`` reach the wire as the same conditional header.

    The rust path does not run the legacy header step, so its prep has to emit
    ``If-Match`` / ``If-None-Match`` itself. Header names are compared
    case-insensitively (both engines lower-case them here) because HTTP header
    names are case-insensitive on the wire.
    """
    options = {"accessCondition": {"type": condition_type, "condition": "etag-1"}}
    _assert_header_parity(options)
    assert _rust_option_headers(options)[expected_header] == "etag-1"


def test_many_options_at_once_stay_in_parity():
    """A realistic multi-option call matches header-for-header.

    Per-key tests can all pass while the combination diverges -- for instance if
    one path let a later option overwrite an earlier one. This is the shape of a
    real ``create_item`` with triggers, an etag, and routing hints.
    """
    _assert_header_parity({
        "preTriggerInclude": ["validate", "audit"],
        "postTriggerInclude": "notify",
        "indexingDirective": "Include",
        "maxItemCount": 50,
        "priorityLevel": "Low",
        "consistencyLevel": "Session",
        "accessCondition": {"type": "IfMatch", "condition": "etag-9"},
        "enableCrossPartitionQuery": True,
        "containerRID": "RID==",
        "correlatedActivityId": "corr-42",
    })


def test_no_response_on_write_maps_to_prefer_on_legacy():
    """``no_response`` becomes ``Prefer: return=minimal`` on the legacy path.

    Excluded from the generic diff because the binding lifts this option to a
    typed driver field instead of a header, so the two are not comparable as
    headers. Pinned here so the legacy half of the contract keeps a test,
    including the detail that legacy applies it only to non-GET ``docs``
    requests -- a read never carries it however the option is set.
    """
    enabled = {"responsePayloadOnWriteDisabled": True}
    write_headers = _legacy_option_headers(enabled, resource_type="docs", verb="post")
    assert write_headers.get("prefer") == "return=minimal"
    # A read (GET) never carries it, whatever the option says.
    read_headers = _legacy_option_headers(enabled, resource_type="docs", verb="get")
    assert "prefer" not in read_headers
    # Nor does a write when the option is off.
    disabled = {"responsePayloadOnWriteDisabled": False}
    assert "prefer" not in _legacy_option_headers(
        disabled, resource_type="docs", verb="post",
    )


# ---------------------------------------------------------------------------
# Guard the guard -- these tests must not rot into no-ops.
# ---------------------------------------------------------------------------


def test_every_rust_handled_key_is_covered_or_explicitly_excluded():
    """No option-key can be added without landing in this file's coverage.

    Without this, someone adds a knob to ``RUST_HANDLED_OPTION_KEYS`` and the
    value-parity suite silently never exercises it. A new key must either get a
    case in ``_TRUTHY_CASES`` or be listed in ``_STRUCTURALLY_EXCLUDED_KEYS``
    with a reason.
    """
    covered = {key for key, _ in _TRUTHY_CASES}
    uncovered = sorted(RUST_HANDLED_OPTION_KEYS - covered - _STRUCTURALLY_EXCLUDED_KEYS)
    assert not uncovered, (
        "These option-keys are in RUST_HANDLED_OPTION_KEYS but this file never "
        f"diffs their header value: {uncovered}. Add a case to _TRUTHY_CASES "
        "(and a falsy one to _FALSY_CASES if the option is truthy-gated), or "
        "add the key to _STRUCTURALLY_EXCLUDED_KEYS with a reason."
    )


def test_excluded_keys_are_still_real_keys():
    """The exclusion list cannot silently outlive the keys it names.

    A stale entry here would quietly shrink the coverage the test above
    enforces, so a renamed or removed key has to be cleaned up.
    """
    stale = sorted(_STRUCTURALLY_EXCLUDED_KEYS - RUST_HANDLED_OPTION_KEYS)
    assert not stale, (
        f"_STRUCTURALLY_EXCLUDED_KEYS names keys that are no longer in "
        f"RUST_HANDLED_OPTION_KEYS: {stale}. Remove them."
    )


def test_rust_mapping_table_actually_parsed():
    """A broken parse must fail loudly instead of making every diff vacuous.

    If the regexes stop matching after a ``wire/request.rs`` refactor, every
    option would appear to map to its own name and the comparisons could pass
    for the wrong reason. Anchor on a few entries that must always be present.
    """
    mapping = _rust_option_key_to_wire_name()
    assert len(mapping) > 20, (
        f"only parsed {len(mapping)} mappings out of extract_op_modifiers; "
        "the regexes in _rust_option_key_to_wire_name are probably broken"
    )
    assert mapping["maxitemcount"] == "x-ms-max-item-count"
    assert mapping["pretriggerinclude"] == "x-ms-documentdb-pre-trigger-include"
    # A wrapped multi-line arm, to prove that branch of the parser works.
    assert mapping["offerenableruperminutethroughput"] == (
        "x-ms-offer-is-ru-per-minute-throughput-enabled"
    )


def test_legacy_baseline_subtraction_leaves_nothing_for_empty_options():
    """An empty options dict yields no option-derived headers on either engine.

    This is what makes the differencing in :func:`_legacy_option_headers`
    trustworthy: if the subtraction were wrong, unconditional headers would leak
    into every comparison and mask real diffs.
    """
    assert _legacy_option_headers({}) == {}
    assert _rust_option_headers({}) == {}


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
