# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import re
import sys
import logging
import functools
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AIProjectClientAsync
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader

"""
Set these environment variables before running the test:
set AZURE_AI_PROJECTS_DIAGNOSTICS_TEST_PROJECT_CONNECTION_STRING=
"""
servicePreparerTelemetryTests = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_telemetry_test",
    azure_ai_projects_telemetry_tests_project_connection_string="region.api.azureml.ms;00000000-0000-0000-0000-000000000000;rg-name;project-name",
)

# Set to True to enable SDK logging
LOGGING_ENABLED = False

if LOGGING_ENABLED:
    # Create a logger for the 'azure' SDK
    # See https://docs.python.org/3/library/logging.html
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)  # INFO or DEBUG

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)


class TelemetryTestBase(AzureRecordedTestCase):

    # Regular expression describing the pattern of an Application Insights connection string.
    REGEX_APPINSIGHTS_CONNECTION_STRING = re.compile(
        r"^InstrumentationKey=[0-9a-fA-F-]{36};IngestionEndpoint=https://.+.applicationinsights.azure.com/;LiveEndpoint=https://.+.monitor.azure.com/;ApplicationId=[0-9a-fA-F-]{36}$"
    )

    def get_sync_client(self, **kwargs) -> AIProjectClient:
        conn_str = kwargs.pop("azure_ai_projects_telemetry_tests_project_connection_string")
        project_client = AIProjectClient.from_connection_string(
            credential=self.get_credential(AIProjectClient, is_async=False),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client

    def get_async_client(self, **kwargs) -> AIProjectClientAsync:
        conn_str = kwargs.pop("azure_ai_projects_telemetry_tests_project_connection_string")
        project_client = AIProjectClientAsync.from_connection_string(
            credential=self.get_credential(AIProjectClientAsync, is_async=True),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client
