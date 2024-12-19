# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy
from connection_test_base import ConnectionsTestBase, servicePreparerConnectionsTests
from azure.ai.projects.models import ConnectionType, AuthenticationType
from azure.core.exceptions import ResourceNotFoundError


# The test class name needs to start with "Test" to get collected by pytest
class TestConnections(ConnectionsTestBase):

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_connections_get(self, **kwargs):

        default_key_auth_aoai_connection = kwargs.pop(
            "azure_ai_projects_connections_tests_default_key_auth_aoai_connection_name"
        )
        default_key_auth_aiservices_connection = kwargs.pop(
            "azure_ai_projects_connections_tests_default_key_auth_aiservices_connection_name"
        )
        entraid_auth_aoai_connection = kwargs.pop(
            "azure_ai_projects_connections_tests_entraid_auth_aoai_connection_name"
        )
        entraid_auth_aiservices_connection = kwargs.pop(
            "azure_ai_projects_connections_tests_entraid_auth_aiservices_connection_name"
        )
        aoai_model_deployment_name = kwargs.pop("azure_ai_projects_connections_tests_aoai_model_deployment_name")
        chat_completions_model_deployment_name = kwargs.pop(
            "azure_ai_projects_connections_tests_chat_completions_model_deployment_name"
        )
        aoai_api_version = kwargs.pop("azure_ai_projects_connections_tests_aoai_api_version")

        with self.get_sync_client(**kwargs) as project_client:

            try:
                _ = project_client.connections.get(connection_name="")
                assert False
            except ValueError as e:
                print(e)
                assert ConnectionsTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_EMPTY_CONNECTION_NAME in e.__str__()

            for include_credentials in [True, False]:

                try:
                    _ = project_client.connections.get(
                        connection_name=ConnectionsTestBase.NON_EXISTING_CONNECTION_NAME,
                        include_credentials=include_credentials,
                    )
                    assert False
                except ResourceNotFoundError as e:
                    print(e)
                    assert ConnectionsTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_NAME in e.message

                connection = project_client.connections.get(
                    connection_name=default_key_auth_aoai_connection, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=default_key_auth_aoai_connection,
                    expected_connection_type=ConnectionType.AZURE_OPEN_AI,
                    expected_authentication_type=AuthenticationType.API_KEY,
                )
                if include_credentials:
                    ConnectionsTestBase.validate_inference(
                        connection, aoai_model_deployment_name, aoai_api_version=aoai_api_version
                    )

                connection = project_client.connections.get(
                    connection_name=entraid_auth_aoai_connection, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=entraid_auth_aoai_connection,
                    expected_connection_type=ConnectionType.AZURE_OPEN_AI,
                    expected_authentication_type=AuthenticationType.ENTRA_ID,
                )
                if include_credentials:
                    ConnectionsTestBase.validate_inference(
                        connection, aoai_model_deployment_name, aoai_api_version=aoai_api_version
                    )

                connection = project_client.connections.get(
                    connection_name=default_key_auth_aiservices_connection, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=default_key_auth_aiservices_connection,
                    expected_connection_type=ConnectionType.AZURE_AI_SERVICES,
                    expected_authentication_type=AuthenticationType.API_KEY,
                )
                if include_credentials:
                    ConnectionsTestBase.validate_inference(connection, chat_completions_model_deployment_name)

                connection = project_client.connections.get(
                    connection_name=entraid_auth_aiservices_connection, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=entraid_auth_aiservices_connection,
                    expected_connection_type=ConnectionType.AZURE_AI_SERVICES,
                    expected_authentication_type=AuthenticationType.ENTRA_ID,
                )
                if include_credentials:
                    ConnectionsTestBase.validate_inference(connection, chat_completions_model_deployment_name)

    @servicePreparerConnectionsTests()
    @recorded_by_proxy
    def test_connections_get_default(self, **kwargs):

        default_aoai_connection = kwargs.pop(
            "azure_ai_projects_connections_tests_default_key_auth_aoai_connection_name"
        )
        default_serverless_connection = kwargs.pop(
            "azure_ai_projects_connections_tests_default_key_auth_aiservices_connection_name"
        )

        with self.get_sync_client(**kwargs) as project_client:

            for include_credentials in [True, False]:
                try:
                    _ = project_client.connections.get_default(
                        connection_type=ConnectionsTestBase.NON_EXISTING_CONNECTION_TYPE,
                        include_credentials=include_credentials,
                    )
                    assert False
                except ResourceNotFoundError as e:
                    print(e)
                    assert ConnectionsTestBase.EXPECTED_EXCEPTION_MESSAGE_FOR_NON_EXISTING_CONNECTION_TYPE in e.message

                connection = project_client.connections.get_default(
                    connection_type=ConnectionType.AZURE_OPEN_AI, include_credentials=include_credentials
                )
                print(connection)
                ConnectionsTestBase.validate_connection(
                    connection,
                    include_credentials,
                    expected_connection_name=default_aoai_connection,
                    expected_connection_type=ConnectionType.AZURE_OPEN_AI,
                )

                connection = project_client.connections.get_default(
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
    @recorded_by_proxy
    def test_connections_list(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client:

            connections = project_client.connections.list()
            count_all = len(connections)
            print(f"====> Listing of all connections (found {count_all}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)
            assert count_all >= 6

            connections = project_client.connections.list(
                connection_type=ConnectionType.AZURE_OPEN_AI,
            )
            count_aoai = len(connections)
            print(f"====> Listing of all Azure Open AI connections (found {count_aoai}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)
            assert count_aoai >= 2

            connections = project_client.connections.list(
                connection_type=ConnectionType.AZURE_AI_SERVICES,
            )
            count_serverless = len(connections)
            print(f"====> Listing of all Serverless connections (found {count_serverless}):")
            for connection in connections:
                print(connection)
                ConnectionsTestBase.validate_connection(connection, False)
            assert count_serverless >= 2
