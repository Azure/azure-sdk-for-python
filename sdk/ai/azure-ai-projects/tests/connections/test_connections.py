# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from tests.test_base import TestBase, servicePreparerConnectionsTests


class TestConnections(TestBase):

    @servicePreparerConnectionsTests()
    def test_connections(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_connections_tests_project_endpoint")
        connection_name = kwargs.pop("azure_ai_projects_connections_tests_connection_name")

        print("Endpoint:", endpoint)
        print("Connection name:", connection_name)

        with DefaultAzureCredential() as credential:

            with AIProjectClient(
                endpoint=endpoint,
                credential=self.get_credential(AIProjectClient, is_async=False),
            ) as project_client:

                print("[test_connections] List all connections")
                empty = True
                for connection in project_client.connections.list():
                    empty = False
                    TestBase.validate_connection(connection, False)
                assert not empty
    
                print("[test_connections] List all connections of a particular type")
                empty = True
                for connection in project_client.connections.list(
                    connection_type=ConnectionType.AZURE_OPEN_AI,
                ):
                    empty = False
                    TestBase.validate_connection(
                        connection, False, expected_connection_type=ConnectionType.AZURE_OPEN_AI
                    )
                assert not empty

                print("[test_connections] Get the default connection of a particular type, without its credentials")
                connection = project_client.connections.get_default(connection_type=ConnectionType.AZURE_OPEN_AI)
                TestBase.validate_connection(connection, False, expected_connection_type=ConnectionType.AZURE_OPEN_AI)

                print("[test_connections] Get the default connection of a particular type, with its credentials")
                connection = project_client.connections.get_default(
                    connection_type=ConnectionType.AZURE_OPEN_AI, include_credentials=True
                )
                TestBase.validate_connection(
                    connection, True, expected_connection_type=ConnectionType.AZURE_OPEN_AI, expected_is_default=True
                )

                print(f"[test_connections] Get the connection named `{connection_name}`, without its credentials")
                connection = project_client.connections.get(connection_name)
                TestBase.validate_connection(connection, False, expected_connection_name=connection_name)

                print(f"[test_connections] Get the connection named `{connection_name}`, with its credentials")
                connection = project_client.connections.get(connection_name, include_credentials=True)
                TestBase.validate_connection(connection, True, expected_connection_name=connection_name)
