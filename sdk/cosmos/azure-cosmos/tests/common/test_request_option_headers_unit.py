# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Check the headers our request preparation builds from each option.

The expected values below are written out. They were taken from the legacy
``_base.GetHeaders`` output on November 5, 2026, so the customer-visible header
contract is unchanged, but the test no longer runs legacy code to get them.

Native serialization is covered separately by Rust reader tests and the
Python/native schema agreement tests.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

import pytest

from azure.cosmos._helpers._request_settings import OPTION_HEADER_NAMES, OPTION_FIELDS
from common.typed_requests import flatten_options_to_headers


# Option keys that are not checked as headers here, and why:
#
#   * ``sessionToken`` -- set from the session container and consistency level,
#     not from this option table.
#   * ``responsePayloadOnWriteDisabled`` -- the binding passes it to the driver's
#     typed ContentResponseOnWrite field, not as a header.
#   * ``excludedLocations`` / ``availabilityStrategy`` -- routing and hedging
#     controls passed to typed driver fields; they are not wire headers.
#   * ``timeout`` -- a client-side deadline, not a header.
#   * ``initialHeaders`` -- the customer's own headers, forwarded as they are.
_STRUCTURALLY_EXCLUDED_KEYS = frozenset({
    "sessionToken",
    "responsePayloadOnWriteDisabled",
    "excludedLocations",
    "availabilityStrategy",
    "timeout",
    "initialHeaders",
})


def _option_headers(options: Mapping[str, Any]) -> Dict[str, str]:
    """Return the prepared headers as strings, the form that reaches the wire."""
    return {name: str(value) for name, value in flatten_options_to_headers(options).items()}


# ---------------------------------------------------------------------------
# A set option produces one header with the expected name and value.
# ---------------------------------------------------------------------------

# (option key, value a customer could pass, expected header name, expected value)
_TRUTHY_CASES = [
    ("indexingDirective", "Include", "x-ms-indexing-directive", "Include"),
    ("maxItemCount", 100, "x-ms-max-item-count", "100"),
    ("priorityLevel", "High", "x-ms-cosmos-priority-level", "High"),
    ("throughputBucket", 2, "x-ms-cosmos-throughput-bucket", "2"),
    ("containerRID", "RID==", "x-ms-cosmos-intended-collection-rid", "RID=="),
    ("maxIntegratedCacheStaleness", 5000, "x-ms-dedicatedgateway-max-age", "5000"),
    ("offerThroughput", 400, "x-ms-offer-throughput", "400"),
    ("autoUpgradePolicy", '{"maxThroughput":4000}',
     "x-ms-cosmos-offer-autopilot-settings", '{"maxThroughput":4000}'),
    ("continuation", "token-1", "x-ms-continuation", "token-1"),
    ("contentType", "application/query+json", "content-type", "application/query+json"),
    ("correlatedActivityId", "corr-1", "x-ms-cosmos-correlated-activityid", "corr-1"),
    ("disableRUPerMinuteUsage", True, "x-ms-documentdb-disable-ru-per-minute-usage", "True"),
    ("enableCrossPartitionQuery", True, "x-ms-documentdb-query-enablecrosspartition", "True"),
    ("enableScanInQuery", True, "x-ms-documentdb-query-enable-scan", "True"),
    ("enableScriptLogging", True, "x-ms-documentdb-script-enable-logging", "True"),
    ("isQueryPlanRequest", True, "x-ms-cosmos-is-query-plan-request", "True"),
    ("offerEnableRUPerMinuteThroughput", True,
     "x-ms-offer-is-ru-per-minute-throughput-enabled", "True"),
    ("offerType", "S1", "x-ms-offer-type", "S1"),
    ("populateIndexMetrics", True, "x-ms-cosmos-populateindexmetrics", "True"),
    ("populatePartitionKeyRangeStatistics", True,
     "x-ms-documentdb-populatepartitionstatistics", "True"),
    ("populateQueryAdvice", True, "x-ms-cosmos-populatequeryadvice", "True"),
    ("populateQueryMetrics", True, "x-ms-documentdb-populatequerymetrics", "True"),
    ("populateQuotaInfo", True, "x-ms-documentdb-populatequotainfo", "True"),
    ("queryVersion", "1.0", "x-ms-cosmos-query-version", "1.0"),
    ("responseContinuationTokenLimitInKb", 8,
     "x-ms-documentdb-responsecontinuationtokenlimitinkb", "8"),
    ("supportedQueryFeatures", "OrderBy", "x-ms-cosmos-supported-query-features", "OrderBy"),
    ("consistencyLevel", "Eventual", "x-ms-consistency-level", "Eventual"),
    ("consistencyLevel", "ConsistentPrefix", "x-ms-consistency-level", "ConsistentPrefix"),
    ("consistencyLevel", "Session", "x-ms-consistency-level", "Session"),
    ("consistencyLevel", "BoundedStaleness", "x-ms-consistency-level", "BoundedStaleness"),
    ("consistencyLevel", "Strong", "x-ms-consistency-level", "Strong"),
]


@pytest.mark.parametrize(
    "option_key,option_value,header_name,header_value", _TRUTHY_CASES,
    ids=[f"{case[0]}-{index}" for index, case in enumerate(_TRUTHY_CASES)],
)
def test_set_option_produces_expected_header_rust(option_key, option_value, header_name, header_value):
    """A set option produces exactly one header with the expected name and value.

    This catches a wrong header name (say ``x-ms-max-items`` instead of
    ``x-ms-max-item-count``) and a wrongly formatted value.
    """
    assert _option_headers({option_key: option_value}) == {header_name: header_value}


# ---------------------------------------------------------------------------
# An empty or false option sends no header at all.
# ---------------------------------------------------------------------------

# For example, ``indexing_directive=IndexingDirective.Default`` is ``0`` and
# ``throughput_bucket=0`` is not a real bucket; both must send nothing rather
# than a header carrying ``"0"``.
_FALSY_CASES = [
    ("indexingDirective", 0),
    ("throughputBucket", 0),
    ("maxItemCount", 0),
    ("maxIntegratedCacheStaleness", 0),
    ("offerThroughput", 0),
    ("responseContinuationTokenLimitInKb", 0),
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
def test_empty_option_sends_no_header_rust(option_key, option_value):
    """An empty or false option sends no header."""
    assert _option_headers({option_key: option_value}) == {}


def test_no_options_send_no_headers_rust():
    """No options means no option headers."""
    assert _option_headers({}) == {}


# ---------------------------------------------------------------------------
# Conditions and combinations.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "condition_type,expected_header",
    [("IfMatch", "if-match"), ("IfNoneMatch", "if-none-match")],
)
def test_access_condition_becomes_conditional_header_rust(condition_type, expected_header):
    """``etag`` / ``match_condition`` become ``If-Match`` / ``If-None-Match``."""
    options = {"accessCondition": {"type": condition_type, "condition": "etag-1"}}
    assert _option_headers(options) == {expected_header: "etag-1"}


def test_many_options_at_once_produce_every_header_rust():
    """A realistic multi-option call produces every expected header.

    Each option can pass on its own while the combination goes wrong, for
    example if a later option overwrote an earlier one. This is the shape of a
    real ``create_item`` with an etag and routing hints.
    """
    assert _option_headers({
        "indexingDirective": "Include",
        "maxItemCount": 50,
        "priorityLevel": "Low",
        "consistencyLevel": "Session",
        "accessCondition": {"type": "IfMatch", "condition": "etag-9"},
        "enableCrossPartitionQuery": True,
        "containerRID": "RID==",
        "correlatedActivityId": "corr-42",
    }) == {
        "x-ms-indexing-directive": "Include",
        "x-ms-max-item-count": "50",
        "x-ms-cosmos-priority-level": "Low",
        "x-ms-consistency-level": "Session",
        "if-match": "etag-9",
        "x-ms-documentdb-query-enablecrosspartition": "True",
        "x-ms-cosmos-intended-collection-rid": "RID==",
        "x-ms-cosmos-correlated-activityid": "corr-42",
    }


# ---------------------------------------------------------------------------
# Keep this file's coverage complete as options are added or removed.
# ---------------------------------------------------------------------------


def test_every_option_key_is_covered_or_explicitly_excluded_rust():
    """A new option key must get a case here or a listed reason to skip it."""
    covered = {case[0] for case in _TRUTHY_CASES}
    uncovered = sorted(OPTION_FIELDS.keys() - covered - _STRUCTURALLY_EXCLUDED_KEYS)
    assert not uncovered, (
        "These option keys are in OPTION_FIELDS but this file never checks "
        f"their header: {uncovered}. Add a case to _TRUTHY_CASES (and to "
        "_FALSY_CASES if an empty value should send nothing), or add the key "
        "to _STRUCTURALLY_EXCLUDED_KEYS with a reason."
    )


def test_excluded_keys_are_still_real_keys_rust():
    """The exclusion list can't keep naming keys that no longer exist."""
    stale = sorted(_STRUCTURALLY_EXCLUDED_KEYS - (OPTION_FIELDS.keys() | {"initialHeaders"}))
    assert not stale, (
        f"_STRUCTURALLY_EXCLUDED_KEYS names keys that are no longer in "
        f"OPTION_FIELDS: {stale}. Remove them."
    )


def test_header_name_table_contains_required_entries_rust():
    """The option-to-header table is complete and has no removed trigger headers."""
    mapping = {key.lower(): value for key, value in OPTION_HEADER_NAMES.items()}
    assert len(mapping) > 20
    assert mapping["maxitemcount"] == "x-ms-max-item-count"
    assert "pretriggerinclude" not in mapping
    assert "posttriggerinclude" not in mapping
    assert mapping["offerenableruperminutethroughput"] == (
        "x-ms-offer-is-ru-per-minute-throughput-enabled"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
