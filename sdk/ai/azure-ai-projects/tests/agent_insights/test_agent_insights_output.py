# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Offline checks for the recorded samples' deterministic output assertions."""

import pytest

from agent_insights.sample_test_helpers import assert_agent_insights_output


ON_DEMAND_OUTPUT = [
    "Created monitor `monitor-test` for agent `test-agent` (enabled=False, run interval=6 hours).",
    "Run status: JobStatus.SUCCEEDED",
    "Traces in window: 10",
    "Traces analyzed: 10",
    "Insights created: 1",
    "Insights updated: 0",
    "Insights reopened: 0",
    "Listed runs: 1",
    "Listed insights: 1",
    "Insight `insight-test`: title=`Require `approval``, severity=AgentInsightSeverity.HIGH, status=AgentInsightStatus.ACTIVE, traces=8.",
    "Recommended action: Check approval first.",
    "Insight status after update: AgentInsightStatus.RESOLVED",
    "Deleted monitor `monitor-test`.",
]

SCHEDULED_OUTPUT = [
    "Created disabled monitor `monitor-test` for agent `test-agent`.",
    "Scheduled monitor enabled: True",
    "Run interval hours: 6.0",
    "Next scheduled run: 2026-09-09T12:00:00+00:00",
    "Deleted scheduled monitor `monitor-test`.",
]


@pytest.mark.parametrize(
    "sample_name,output,label",
    [
        ("on_demand", ON_DEMAND_OUTPUT, "Monitor"),
        ("scheduled", SCHEDULED_OUTPUT, "Scheduled monitor"),
    ],
)
@pytest.mark.parametrize("already_deleted", [False, True])
def test_sample_output_requires_successful_deletion(sample_name, output, label, already_deleted):
    output = list(output)
    if already_deleted:
        output[-1] = f"{label} `monitor-test` was already deleted."
        with pytest.raises(AssertionError, match="did not clean up"):
            assert_agent_insights_output(f"sample_agent_insights_{sample_name}.py", output)
    else:
        assert_agent_insights_output(f"sample_agent_insights_{sample_name}.py", output)


@pytest.mark.parametrize("removed_line", range(len(ON_DEMAND_OUTPUT)))
def test_rejects_missing_on_demand_contract_fields(removed_line):
    output = ON_DEMAND_OUTPUT[:removed_line] + ON_DEMAND_OUTPUT[removed_line + 1 :]
    with pytest.raises(AssertionError):
        assert_agent_insights_output("sample_agent_insights_on_demand.py", output)


@pytest.mark.parametrize(
    "old,new",
    [
        ("Traces analyzed: 10", "Traces analyzed: 0"),
        ("Traces analyzed: 10", "Traces analyzed: 11"),
        ("Insights created: 1", "Insights created: 0"),
        ("Listed insights: 1", "Listed insights: 2"),
        ("severity=AgentInsightSeverity.HIGH", "severity=None"),
        ("traces=8", "traces=0"),
        ("Check approval first.", "None"),
        ("Deleted monitor `monitor-test`.", "Deleted monitor `old-monitor`."),
        ("Run status: JobStatus.SUCCEEDED", "Run status: JobStatus.CANCELLED"),
        (
            "Insight status after update: AgentInsightStatus.RESOLVED",
            "Insight status after update: AgentInsightStatus.ACTIVE",
        ),
    ],
)
def test_rejects_incomplete_on_demand_workflow(old, new):
    output = [line.replace(old, new) for line in ON_DEMAND_OUTPUT]
    with pytest.raises(AssertionError):
        assert_agent_insights_output("sample_agent_insights_on_demand.py", output)


@pytest.mark.parametrize("removed_line", range(len(SCHEDULED_OUTPUT)))
def test_rejects_missing_scheduled_contract_fields(removed_line):
    output = SCHEDULED_OUTPUT[:removed_line] + SCHEDULED_OUTPUT[removed_line + 1 :]
    with pytest.raises(AssertionError):
        assert_agent_insights_output("sample_agent_insights_scheduled.py", output)


@pytest.mark.parametrize(
    "old,new",
    [
        ("enabled: True", "enabled: False"),
        ("hours: 6.0", "hours: 1"),
        ("2026-09-09T12:00:00+00:00", "None"),
        ("2026-09-09T12:00:00+00:00", "2026-09-09T12:00:00"),
        ("`monitor-test`.", "`old-monitor`."),
    ],
)
def test_rejects_incomplete_scheduled_workflow(old, new):
    output = [line.replace(old, new) for line in SCHEDULED_OUTPUT]
    with pytest.raises(AssertionError):
        assert_agent_insights_output("sample_agent_insights_scheduled.py", output)
