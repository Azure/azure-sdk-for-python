# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Recording sanitizers for Agent Insights identifiers."""

from contextlib import contextmanager
from itertools import count
from unittest.mock import patch

from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from devtools_testutils import (
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
)


@contextmanager
def agent_insights_sample_sanitizers():
    """Keep self-contained sample data private without changing other recordings."""
    add_general_regex_sanitizer(
        regex=r"\bagent-insights-sample-[0-9a-f]{32}\b",
        value="agent-insights-sample-" + "0" * 32,
        function_scoped=True,
    )
    add_general_regex_sanitizer(
        regex=r"(?i)/providers/microsoft\.insights/",
        value="/providers/microsoft.insights/",
        function_scoped=True,
    )
    for path in ("$.instance_identity.*", "$.blueprint.*", "$.agent_guid"):
        add_body_key_sanitizer(
            json_path=path,
            value="00000000-0000-0000-0000-000000000000",
            condition={"uriRegex": r"/agents/agent-insights-sample-[0-9a-f]{32}/versions"},
            function_scoped=True,
        )
    add_header_regex_sanitizer(
        key="Request-Context",
        regex=r"(?i)appId=(?:cid-v1:)?([0-9a-f-]{36})",
        group_for_replace="1",
        value="00000000-0000-0000-0000-000000000000",
        function_scoped=True,
    )
    connection_condition = {"uriRegex": r"/connections(?:/|\?)"}
    connection_string = (
        "InstrumentationKey=00000000-0000-0000-0000-000000000000;"
        "IngestionEndpoint=https://sanitized.in.applicationinsights.azure.com/;"
        "LiveEndpoint=https://sanitized.livediagnostics.monitor.azure.com/;"
        "ApplicationId=00000000-0000-0000-0000-000000000000"
    )
    for path in ("$..credentials.key", "$..metadata.ApplicationInsightsConnectionString"):
        add_body_key_sanitizer(
            json_path=path,
            value=connection_string,
            condition=connection_condition,
            function_scoped=True,
        )
    add_general_regex_sanitizer(
        regex=r"/connections/([^/?\"\\]+)",
        group_for_replace="1",
        value="sanitized-application-insights-connection",
        condition=connection_condition,
        function_scoped=True,
    )
    for path in ("$..name", "$..metadata.displayName"):
        add_body_key_sanitizer(
            json_path=path,
            value="sanitized-application-insights-connection",
            condition=connection_condition,
            function_scoped=True,
        )
    telemetry_condition = {"uriRegex": r"\.in\.applicationinsights\.azure\.com/+v2\.1/track"}
    for path, value in (
        ("$[*].iKey", "00000000-0000-0000-0000-000000000000"),
        ("$[*].time", "2026-01-01T00:00:00.000000Z"),
        ("$[*].data.baseData.duration", "0.00:00:00.001"),
        ("$[*].data.baseData.properties['microsoft.applicationId']", "00000000-0000-0000-0000-000000000000"),
        ("$[*].tags['ai.device.id']", "sanitized-device"),
        ("$[*].tags['ai.device.locale']", "sanitized-locale"),
        ("$[*].tags['ai.internal.nodeName']", "sanitized-device"),
        ("$[*].tags['ai.internal.sdkVersion']", "sanitized-sdk-version"),
    ):
        add_body_key_sanitizer(
            json_path=path,
            value=value,
            condition=telemetry_condition,
            function_scoped=True,
        )

    def sanitize_id(original, width):
        identifiers = count(1)

        def generate(generator):
            identifier = original(generator)
            # Keep real random IDs in Azure, but preserve the trace tree in playback.
            add_general_regex_sanitizer(
                regex=rf"\b{identifier:0{width}x}\b",
                value=f"{next(identifiers):0{width}x}",
                condition=telemetry_condition,
                function_scoped=True,
            )
            return identifier

        return generate

    with (
        patch.object(RandomIdGenerator, "generate_trace_id", sanitize_id(RandomIdGenerator.generate_trace_id, 32)),
        patch.object(RandomIdGenerator, "generate_span_id", sanitize_id(RandomIdGenerator.generate_span_id, 16)),
    ):
        yield


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
