# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Recording sanitizers for Agent Insights identifiers."""

from devtools_testutils import (
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
)


def add_agent_insights_sanitizers() -> None:
    add_header_regex_sanitizer(
        key="Operation-Id",
        regex=r".+",
        value="00000000-0000-0000-0000-000000000000",
    )
    add_general_regex_sanitizer(
        regex=r"\bmonitor_[0-9a-f-]{32,36}\b",
        value="monitor_00000000000000000000000000000000",
    )
    add_general_regex_sanitizer(
        regex=r"\brun_[0-9a-f-]{32,36}\b",
        value="run_00000000000000000000000000000000",
    )
    add_general_regex_sanitizer(
        regex=r"\binsight_[0-9a-f]{24,64}\b",
        value="insight_000000000000000000000000",
    )
    add_body_key_sanitizer(
        json_path="$..trace_id",
        value="00000000000000000000000000000000",
    )
    add_general_regex_sanitizer(
        regex=r"https://(?:agent-insights|Sanitized)\.[a-z0-9-]+\.hyena\.infra\.ai\.azure\.com",
        value="https://sanitized-agent-insights.azure.com",
    )
