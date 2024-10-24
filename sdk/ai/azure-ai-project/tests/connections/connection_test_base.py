# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import logging
import functools
from azure.ai.project import AIProjectClient
from azure.identity import DefaultAzureCredential
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader

ServicePreparerChatCompletions = functools.partial(
    EnvironmentVariableLoader,
    "project_connection_string",
    project_connection_string_connections_tests="endpoint;azure-subscription-id;azure-rg-name;ai-studio-hub-name",
)

# Set to True to enable SDK logging
LOGGING_ENABLED = True

if LOGGING_ENABLED:
    # Create a logger for the 'azure' SDK
    # See https://docs.python.org/3/library/logging.html
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)  # INFO or DEBUG

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

class ConnectionsTestBase:

    def get_sync_client(self, **kwargs) -> AIProjectClient:
        conn_str = kwargs.pop("project_connection_string_connections_tests")
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=conn_str,
        )
        return project_client

