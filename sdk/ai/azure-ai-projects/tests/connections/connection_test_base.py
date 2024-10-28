# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import logging
import functools
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader

"""
Set these environment variables before running the test:
set AZURE_AI_PROJECTS_CONNECTIONS_TESTS_PROJECT_CONNECTION_STRING=
"""
servicePreparerConnectionsTests = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_connections_tests",
    azure_ai_projects_connections_tests_project_connection_string="azure-region.api.azureml.ms;00000000-0000-0000-0000-000000000000;rg-name;hub-name",
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


class ConnectionsTestBase(AzureRecordedTestCase):

    def get_sync_client(self, **kwargs) -> AIProjectClient:
        conn_str = kwargs.pop("azure_ai_projects_connections_tests_project_connection_string")
        project_client = AIProjectClient.from_connection_string(
            credential=self.get_credential(AIProjectClient, is_async=False),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client
