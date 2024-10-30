# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from connection_test_base import ConnectionsTestBase, servicePreparerConnectionsTests
from azure.ai.projects.models import ConnectionType


# The test class name needs to start with "Test" to get collected by pytest
class TestConnections(ConnectionsTestBase):

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_connections_get(self, **kwargs):

        aoai_connection = kwargs.pop("azure_ai_projects_connections_tests_aoai_connection_name")
        serverless_connection = kwargs.pop("azure_ai_projects_connections_tests_serverless_connection_name")

        with self.get_sync_client(**kwargs) as project_client:

            connection = project_client.connections.get(connection_name=aoai_connection, with_credentials=False)
            print(connection)
            ConnectionsTestBase.validate_connection(
                connection,
                False,
                expected_connection_name=aoai_connection,
                expected_connection_type=ConnectionType.AZURE_OPEN_AI,
            )

            connection = project_client.connections.get(connection_name=aoai_connection, with_credentials=True)
            print(connection)
            ConnectionsTestBase.validate_connection(
                connection,
                True,
                expected_connection_name=aoai_connection,
                expected_connection_type=ConnectionType.AZURE_OPEN_AI,
            )

            connection = project_client.connections.get(connection_name=serverless_connection, with_credentials=False)
            print(connection)
            ConnectionsTestBase.validate_connection(
                connection,
                False,
                expected_connection_name=serverless_connection,
                expected_connection_type=ConnectionType.SERVERLESS,
            )

            connection = project_client.connections.get(connection_name=serverless_connection, with_credentials=True)
            print(connection)
            ConnectionsTestBase.validate_connection(
                connection,
                True,
                expected_connection_name=serverless_connection,
                expected_connection_type=ConnectionType.SERVERLESS,
            )

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_connections_get_default(self, **kwargs):

        default_aoai_connection = kwargs.pop("azure_ai_projects_connections_tests_default_aoai_connection_name")
        default_serverless_connection = kwargs.pop(
            "azure_ai_projects_connections_tests_default_serverless_connection_name"
        )

        with self.get_sync_client(**kwargs) as project_client:

            connection = project_client.connections.get_default(
                connection_type=ConnectionType.AZURE_OPEN_AI, with_credentials=False
            )
            print(connection)
            ConnectionsTestBase.validate_connection(
                connection,
                False,
                expected_connection_name=default_aoai_connection,
                expected_connection_type=ConnectionType.AZURE_OPEN_AI,
            )

            connection = project_client.connections.get_default(
                connection_type=ConnectionType.AZURE_OPEN_AI, with_credentials=True
            )
            print(connection)
            ConnectionsTestBase.validate_connection(
                connection,
                True,
                expected_connection_name=default_aoai_connection,
                expected_connection_type=ConnectionType.AZURE_OPEN_AI,
            )

            connection = project_client.connections.get_default(
                connection_type=ConnectionType.SERVERLESS, with_credentials=False
            )
            print(connection)
            ConnectionsTestBase.validate_connection(
                connection,
                False,
                expected_connection_name=default_serverless_connection,
                expected_connection_type=ConnectionType.SERVERLESS,
            )

            connection = project_client.connections.get_default(
                connection_type=ConnectionType.SERVERLESS, with_credentials=True
            )
            print(connection)
            ConnectionsTestBase.validate_connection(
                connection,
                True,
                expected_connection_name=default_serverless_connection,
                expected_connection_type=ConnectionType.SERVERLESS,
            )

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_connections_list(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:

            connections = project_client.connections.list()
            count_all = len(connections)
            print(f"====> Listing of all connections (found {count_all}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)

            connections = project_client.connections.list(
                connection_type=ConnectionType.AZURE_OPEN_AI,
            )
            count_aoai = len(connections)
            print("====> Listing of all Azure Open AI connections (found {count_aoai}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)

            connections = project_client.connections.list(
                connection_type=ConnectionType.SERVERLESS,
            )
            count_serverless = len(connections)
            print("====> Listing of all Serverless connections (found {count_serverless}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)

            assert count_all > 2
            assert count_all > count_aoai
            assert count_all > count_serverless
