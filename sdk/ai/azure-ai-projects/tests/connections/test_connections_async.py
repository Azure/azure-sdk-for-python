# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import ConnectionType
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async


class TestConnectionsAsync(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\connections\test_connections_async.py::TestConnectionsAsync::test_connections_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_connections_async(self, **kwargs):

        connection_type = ConnectionType.AZURE_OPEN_AI

        async with self.create_async_client(**kwargs) as project_client:

            print("[test_connections_async] List all connections")
            empty = True
            async for connection in project_client.connections.list():
                empty = False
                TestBase.validate_connection(connection, False)
            assert not empty

            print("[test_connections_async] List all connections of a particular type")
            empty = True
            async for connection in project_client.connections.list(
                connection_type=connection_type,
            ):
                empty = False
                TestBase.validate_connection(connection, False, expected_connection_type=connection_type)
            assert not empty

            print("[test_connections_async] Get the default connection of a particular type, without its credentials")
            connection = await project_client.connections.get_default(connection_type=connection_type)
            TestBase.validate_connection(connection, False, expected_connection_type=connection_type)

            print("[test_connections_async] Get the default connection of a particular type, with its credentials")
            connection = await project_client.connections.get_default(
                connection_type=connection_type, include_credentials=True
            )
            TestBase.validate_connection(
                connection, True, expected_connection_type=connection_type, expected_is_default=True
            )

            print(f"[test_connections_async] Get the connection named `{connection.name}`, without its credentials")
            connection = await project_client.connections.get(connection.name)
            TestBase.validate_connection(connection, False, expected_connection_name=connection.name)

            print(f"[test_connections_async] Get the connection named `{connection.name}`, with its credentials")
            connection = await project_client.connections.get(connection.name, include_credentials=True)
            TestBase.validate_connection(connection, True, expected_connection_name=connection.name)
