# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils.aio import recorded_by_proxy_async
from connection_test_base import ConnectionsTestBase, servicePreparerConnectionsTests
from azure.ai.projects.models import ConnectionType
from azure.core.exceptions import ResourceNotFoundError


# The test class name needs to start with "Test" to get collected by pytest
class TestConnectionsAsync(ConnectionsTestBase):

    @servicePreparerConnectionsTests()
    @recorded_by_proxy_async
    async def test_connections_get_async(self, **kwargs):
        aoai_connection = kwargs.pop("azure_ai_projects_connections_tests_aoai_connection_name")
        aiservices_connection = kwargs.pop("azure_ai_projects_connections_tests_aiservices_connection_name")

        async with self.get_async_client(**kwargs) as project_client:

            for include_credentials in [True, False]:
                try:
                    _ = await project_client.connections.get(
                        connection_name=ConnectionsTestBase.NON_EXISTING_CONNECTION_NAME,
                        include_credentials=include_credentials,
                    )
                    assert False
                except ResourceNotFoundError as e:
                    print(e)
                    assert ConnectionsTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message

                connection = await project_client.connections.get(
                    connection_name=aoai_connection, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=aoai_connection,
                    expected_connection_type=ConnectionType.AZURE_OPEN_AI,
                )

                connection = await project_client.connections.get(
                    connection_name=aiservices_connection, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=aiservices_connection,
                    expected_connection_type=ConnectionType.AZURE_AI_SERVICES,
                )

    @servicePreparerConnectionsTests()
    @recorded_by_proxy_async
    async def test_connections_get_default_async(self, **kwargs):

        default_aoai_connection = kwargs.pop("azure_ai_projects_connections_tests_aoai_connection_name")
        default_serverless_connection = kwargs.pop("azure_ai_projects_connections_tests_aiservices_connection_name")

        async with self.get_async_client(**kwargs) as project_client:

            for include_credentials in [True, False]:
                try:
                    _ = await project_client.connections.get_default(
                        connection_type=ConnectionsTestBase.NON_EXISTING_CONNECTION_TYPE,
                        include_credentials=include_credentials,
                    )
                    assert False
                except ResourceNotFoundError as e:
                    print(e)
                    assert ConnectionsTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_TYPE in e.message

                connection = await project_client.connections.get_default(
                    connection_type=ConnectionType.AZURE_OPEN_AI, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=default_aoai_connection,
                    expected_connection_type=ConnectionType.AZURE_OPEN_AI,
                )

                connection = await project_client.connections.get_default(
                    connection_type=ConnectionType.AZURE_AI_SERVICES, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=default_serverless_connection,
                    expected_connection_type=ConnectionType.AZURE_AI_SERVICES,
                )

    @servicePreparerConnectionsTests()
    @recorded_by_proxy_async
    async def test_connections_list_async(self, **kwargs):
        async with self.get_async_client(**kwargs) as project_client:

            connections = await project_client.connections.list()
            count_all = len(connections)
            print(f"====> Listing of all connections (found {count_all}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)

            connections = await project_client.connections.list(
                connection_type=ConnectionType.AZURE_OPEN_AI,
            )
            count_aoai = len(connections)
            print(f"====> Listing of all Azure Open AI connections (found {count_aoai}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)

            connections = await project_client.connections.list(
                connection_type=ConnectionType.AZURE_AI_SERVICES,
            )
            count_serverless = len(connections)
            print(f"====> Listing of all Serverless connections (found {count_serverless}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)

            assert count_all > 2
            assert count_all > count_aoai
            assert count_all > count_serverless
