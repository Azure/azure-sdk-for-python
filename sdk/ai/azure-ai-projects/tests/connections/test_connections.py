# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.ai.projects.models import ConnectionType, CredentialType, CustomCredential
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy


@pytest.mark.skip(
    reason="Skipped until re-enabled and recorded on Foundry endpoint that supports the new versioning schema"
)
class TestConnections(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\connections\test_connections.py::TestConnections::test_connections -s
    @servicePreparer()
    @recorded_by_proxy
    def test_connections(self, **kwargs):

        connection_name = kwargs["mcp_project_connection_id"].split("/")[-1]
        connection_type = ConnectionType.AZURE_OPEN_AI

        with self.create_client(**kwargs) as project_client:

            print("[test_connections] List all connections")
            empty = True
            for connection in project_client.connections.list():
                empty = False
                TestBase.validate_connection(connection, False)
            assert not empty

            print("[test_connections] List all connections of a particular type")
            empty = True
            for connection in project_client.connections.list(
                connection_type=connection_type,
            ):
                empty = False
                TestBase.validate_connection(connection, False, expected_connection_type=connection_type)
            assert not empty

            print("[test_connections] Get the default connection of a particular type, without its credentials")
            connection = project_client.connections.get_default(connection_type=connection_type)
            TestBase.validate_connection(connection, False, expected_connection_type=connection_type)

            print("[test_connections] Get the default connection of a particular type, with its credentials")
            connection = project_client.connections.get_default(
                connection_type=connection_type, include_credentials=True
            )
            TestBase.validate_connection(
                connection, True, expected_connection_type=connection_type, expected_is_default=True
            )

            print(f"[test_connections] Get the connection named `{connection_name}`, without its credentials")
            connection = project_client.connections.get(connection_name)
            TestBase.validate_connection(connection, False, expected_connection_name=connection_name)

            print(f"[test_connections] Get the connection named `{connection_name}`, with its credentials")
            connection = project_client.connections.get(connection_name, include_credentials=True)
            TestBase.validate_connection(connection, True, expected_connection_name=connection_name)

    # Unit-test for patched initialization method in CustomCredential class.
    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\connections\test_connections.py::TestConnections::test_custom_credential_deserialization -s
    def test_custom_credential_deserialization(self):

        # Case 1: credentials payload WITH secret keys (in addition to the "type" discriminator)
        payload_with_keys = {
            "key1": "value1",
            "key2": "value2",
            "type": "CustomKeys",
        }
        cred_with_keys = CustomCredential(payload_with_keys)
        assert cred_with_keys.type == CredentialType.CUSTOM
        assert cred_with_keys.credential_keys == {"key1": "value1", "key2": "value2"}

        # Case 2: credentials payload WITHOUT secret keys (only the "type" discriminator)
        payload_without_keys = {
            "type": "CustomKeys",
        }
        cred_without_keys = CustomCredential(payload_without_keys)
        assert cred_without_keys.type == CredentialType.CUSTOM
        assert cred_without_keys.credential_keys == {}
