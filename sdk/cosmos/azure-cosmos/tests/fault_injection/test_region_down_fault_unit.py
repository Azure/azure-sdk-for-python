# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline safeguards; only live runs establish outage and failover behavior."""

import json

import pytest

from fault_injection._region_down import CASES, assert_fault_evidence, outage_rules
from fault_injection._regional_routing import READ_REGION, WRITE_REGION, expected_regions


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("inject", [True, False])
def test_outage_and_control_keep_topology_and_scope_rust(case, inject):
    configured = outage_rules(case, "scenario", "orders", "https://127.0.0.1:8081/", "https://localhost:8081/", inject)
    metadata, *faults = configured
    assert metadata["operation_type"] == "MetadataReadDatabaseAccount"
    assert metadata["status_code"] == 200 and metadata["probability"] == 1
    account = json.loads(metadata["response_body"])
    multi_write = case in ("mwr-down", "all-down")
    assert account["enableMultipleWriteLocations"] is multi_write
    assert [region["name"] for region in account["writableLocations"]] == (
        [WRITE_REGION, READ_REGION] if multi_write else [WRITE_REGION]
    )
    assert all(rule["container_id"] == "orders" and rule["hit_limit"] is None for rule in faults)
    outages = [rule for rule in faults if "-outage-" in rule["id"]]
    assert all(rule["probability"] == float(inject) for rule in outages)
    assert {rule["region"] for rule in outages} == (
        {WRITE_REGION, READ_REGION}
        if case in ("all-reads-down", "all-down")
        else {WRITE_REGION} if multi_write else {READ_REGION}
    )
    assert {rule["operation_type"] for rule in outages} == ({"UpsertItem", "ReadItem"} if multi_write else {"ReadItem"})
    for rule in outages:
        if case == "read-envoy":
            assert rule["status_code"] == 502 and rule["delay_ms"] == 500
            assert "error_type" not in rule
        else:
            assert rule["error_type"] == "ConnectionError"
            assert "status_code" not in rule
    guards = [rule for rule in faults if "-outage-" not in rule["id"]]
    assert len(guards) == (0 if multi_write else 2)
    assert all((rule["region"], rule["status_code"], rule["sub_status"]) == (READ_REGION, 403, 3) for rule in guards)
    assert len({rule["id"] for rule in configured}) == len(configured)
    assert expected_regions(False, multi_write)[0] == (["eastus", "westus"] if multi_write else ["eastus"])


def test_outage_evidence_requires_every_failed_region_and_matches_named_hits_rust():
    configured = outage_rules("all-reads-down", "case", "orders", "https://127.0.0.1/", "https://localhost/", True)
    counts = {rule["id"]: int("-outage-" in rule["id"]) for rule in configured[1:]}
    attempts = [{"evaluations": [{"rule_id": name, "applied": True}]} for name, count in counts.items() if count]
    assert_fault_evidence(configured, counts, attempts, True)
    with pytest.raises(AssertionError, match="Missing attempt"):
        assert_fault_evidence(configured, counts, attempts[:-1], True)
    missing = {**counts, attempts[-1]["evaluations"][0]["rule_id"]: 0}
    with pytest.raises(AssertionError, match="was not exercised"):
        assert_fault_evidence(configured, missing, attempts[:-1], True)
    with pytest.raises(AssertionError, match="Unexpected fault"):
        assert_fault_evidence(configured, counts, attempts, False)
    assert_fault_evidence(configured, dict.fromkeys(counts, 0), [], False)


def test_outage_rule_generation_does_not_share_mutable_topology_rust():
    first = outage_rules("all-down", "first", "one", "https://127.0.0.1/", "https://localhost/", True)
    second = outage_rules("read-down", "second", "two", "https://127.0.0.1/", "https://localhost/", False)
    assert len(json.loads(first[0]["response_body"])["writableLocations"]) == 2
    assert len(json.loads(second[0]["response_body"])["writableLocations"]) == 1
    assert {rule["id"] for rule in first}.isdisjoint(rule["id"] for rule in second)
    with pytest.raises(ValueError, match="Unknown regional outage"):
        outage_rules("typo", "bad", "orders", "", "", True)
