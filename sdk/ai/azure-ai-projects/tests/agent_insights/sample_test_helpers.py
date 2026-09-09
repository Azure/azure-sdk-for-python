# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Test configuration and output checks for the Agent Insights samples."""

import functools
import os
import re
from datetime import datetime

from devtools_testutils import EnvironmentVariableLoader


agentInsightsServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    foundry_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    foundry_agent_name="sanitized-agent-name",
    foundry_model_name="sanitized-model-deployment-name",
)


def assert_agent_insights_output(sample_path: str, print_output_calls: list[str]) -> None:
    """Check the sample's observable contract without interpreting generated prose."""
    output = "\n".join(print_output_calls)
    sample_name = os.path.basename(sample_path)
    scheduled = sample_name == "sample_agent_insights_scheduled.py"
    assert scheduled or sample_name == "sample_agent_insights_on_demand.py", sample_name
    created = re.search(r"^Created (?:disabled )?monitor `([^`]+)` for agent `([^`]+)`", output, re.MULTILINE)
    assert created is not None, "The sample did not create a monitor for an agent."
    monitor_id = re.escape(created.group(1))
    label = "scheduled monitor" if scheduled else "monitor"
    assert re.search(
        rf"^Deleted {label} `{monitor_id}`\.$",
        output,
        re.MULTILINE,
    ), "The sample did not clean up its new monitor."

    if scheduled:
        assert re.search(r"^Scheduled monitor enabled: True$", output, re.MULTILINE)
        interval = re.search(r"^Run interval hours: ([0-9]+(?:\.[0-9]+)?)$", output, re.MULTILINE)
        assert interval is not None and float(interval.group(1)) == 6, "The schedule must run every six hours."
        next_run = re.search(r"^Next scheduled run: (.+)$", output, re.MULTILINE)
        assert next_run is not None, "The schedule must have a next run time."
        try:
            timestamp = datetime.fromisoformat(next_run.group(1))
        except ValueError as error:
            raise AssertionError("The next run time must be an ISO timestamp.") from error
        assert timestamp.utcoffset() is not None, "The next run time must include a time zone."
        return

    assert re.search(r"^Run status: succeeded$", output, re.MULTILINE), "The run did not succeed."

    def read_count(label: str) -> int:
        match = re.search(rf"^{re.escape(label)}: (\d+)$", output, re.MULTILINE)
        assert match is not None, f"The sample did not print '{label}'."
        return int(match.group(1))

    assert 0 < read_count("Traces analyzed") <= read_count("Traces in window")
    assert read_count("Insights created") + read_count("Insights updated") + read_count("Insights reopened") > 0
    assert read_count("Listed runs") > 0
    insight_count = read_count("Listed insights")
    assert insight_count > 0
    insights = re.findall(
        r"^Insight `([^`]+)`: title=`(.+)`, severity=(low|medium|high), "
        r"status=(active|resolved|ignored), traces=([1-9]\d*)\.$",
        output,
        re.MULTILINE,
    )
    assert len(insights) == insight_count, "Every listed insight must have populated detail fields."
    assert all(title.strip() for _, title, *_ in insights)
    assert len(re.findall(r"^Recommended action: (?!None$)\S.*$", output, re.MULTILINE)) == insight_count
    assert re.search(r"^Insight status after update: resolved$", output, re.MULTILINE)
    assert re.search(r"^Insight status after reopening: active$", output, re.MULTILINE)
