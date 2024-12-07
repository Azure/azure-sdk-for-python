# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import logging
import functools
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AIProjectClientAsync
from azure.ai.projects.models import ConnectionProperties, ConnectionType, AuthenticationType
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader


servicePreparerConnectionsTests = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_connections_tests",
    azure_ai_projects_connections_tests_project_connection_string="region.api.azureml.ms;00000000-0000-0000-0000-000000000000;rg-name;project-name",
    azure_ai_projects_connections_tests_aoai_connection_name="aoai-connection-name",
    azure_ai_projects_connections_tests_aiservices_connection_name="aiservices-connection-name",
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

    NON_EXISTING_CONNECTION_NAME = "non-existing-connection-name"
    EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME = (
        f"Connection {NON_EXISTING_CONNECTION_NAME} can't be found in this workspace"
    )

    NON_EXISTING_CONNECTION_TYPE = "non-existing-connection-type"
    EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_TYPE = (
        f"No connection of type {NON_EXISTING_CONNECTION_TYPE} found"
    )

    def get_sync_client(self, **kwargs) -> AIProjectClient:
        conn_str = kwargs.pop("azure_ai_projects_connections_tests_project_connection_string")
        project_client = AIProjectClient.from_connection_string(
            credential=self.get_credential(AIProjectClient, is_async=False),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client

    def get_async_client(self, **kwargs) -> AIProjectClientAsync:
        conn_str = kwargs.pop("azure_ai_projects_connections_tests_project_connection_string")
        project_client = AIProjectClientAsync.from_connection_string(
            credential=self.get_credential(AIProjectClient, is_async=True),
            conn_str=conn_str,
            logging_enable=LOGGING_ENABLED,
        )
        return project_client

    @classmethod
    def validate_connection(
        cls,
        connection: ConnectionProperties,
        include_credentials: bool,
        *,
        expected_connection_type: ConnectionType = None,
        expected_connection_name: str = None,
        expected_authentication_type: AuthenticationType = None,
    ):
        assert connection.id is not None

        if expected_connection_name:
            assert connection.name == expected_connection_name
        else:
            assert connection.name is not None

        if expected_connection_type:
            assert connection.connection_type == expected_connection_type
        else:
            assert connection.connection_type is not None

        if expected_authentication_type:
            assert connection.authentication_type == expected_authentication_type
        else:
            assert connection.authentication_type is not None

        if include_credentials:
            assert (connection.key is not None) ^ (connection.token_credential is not None)
        else:
            assert connection.key == None
            assert connection.token_credential == None
