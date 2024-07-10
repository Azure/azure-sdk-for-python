# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable, Tuple

from time import sleep
import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient, load_connection, load_datastore
from azure.ai.ml._restclient.v2024_04_01_preview.models import ConnectionAuthType, ConnectionCategory
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import (
    WorkspaceConnection,
    Workspace,
    Hub,
    ApiKeyConfiguration,
    AzureBlobDatastore,
    AzureBlobStoreConnection,
    AzureBlobStoreConnection,
    MicrosoftOneLakeConnection,
    AzureOpenAIConnection,
    AzureAIServicesConnection,
    AzureAISearchConnection,
    AzureContentSafetyConnection,
    AzureSpeechServicesConnection,
    APIKeyConnection,
    OpenAIConnection,
    SerpConnection,
    ServerlessConnection,
    AccountKeyConfiguration,
)
from azure.ai.ml.constants._common import ConnectionTypes
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml.entities._datastore.datastore import Datastore


@pytest.mark.xdist_group(name="connection")
@pytest.mark.e2etest
@pytest.mark.core_sdk_test
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceConnections(AzureRecordedTestCase):
    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_secret_population(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(source="./tests/test_configs/connection/azure_open_ai_api.yaml")
        wps_connection.name = wps_connection_name
        wps_connection.open_ai_resource_id = None  # Not dealing with finding a valid ID for this test
        # Not sure what this is, some sort of scrubbed/injected value
        assert wps_connection.credentials.key == "12344"

        try:
            expected_key = "12344" if is_live() else "dGhpcyBpcyBmYWtlIGtleQ=="
            created_conn_with_key = client.connections.create_or_update(
                workspace_connection=wps_connection, populate_secrets=True
            )
            created_conn_no_key = client.connections.create_or_update(workspace_connection=wps_connection)
            sleep(5)  # Give a little time before we start searching for a newly created connection
            assert created_conn_with_key.credentials.key == expected_key
            assert created_conn_no_key.credentials.key == None

            gotten_conn_with_key = client.connections.get(name=wps_connection_name, populate_secrets=True)
            gotten_conn_no_key = client.connections.get(name=wps_connection_name)
            assert gotten_conn_with_key.credentials.key == expected_key
            assert gotten_conn_no_key.credentials.key == None

            listed_conn_with_key = [
                conn for conn in client.connections.list(populate_secrets=True) if conn.name == wps_connection_name
            ][0]
            listed_conn_no_key = [conn for conn in client.connections.list() if conn.name == wps_connection_name][0]
            assert listed_conn_with_key.credentials.key == expected_key
            assert listed_conn_no_key.credentials.key == None

        finally:
            client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_git_pat(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(source="./tests/test_configs/connection/git_pat.yaml")

        wps_connection.name = wps_connection_name

        try:
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.GIT)
            # TODO : Uncomment once service side returns creds correctly
            # assert wps_connection.credentials.pat == "dummy_pat"

            wps_connection.credentials.pat = "dummpy_pat_update"
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.GIT)

            wps_connection = client.connections.get(name=wps_connection_name)
            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.GIT)
            assert wps_connection.metadata == {}
            # TODO : Uncomment once service side returns creds correctly
            # assert wps_connection.credentials.pat == "dummpy_pat_update"
        finally:
            client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_workspace_connections_create_update_and_delete_snowflake_user_pwd(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(source="./tests/test_configs/connection/snowflake_user_pwd.yaml")

        wps_connection.name = wps_connection_name

        try:
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.SNOWFLAKE)
            assert wps_connection.metadata == {}

            wps_connection.credentials.username = "dummy"
            wps_connection.credentials.password = "dummy"
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.SNOWFLAKE)

            wps_connection = client.connections.get(name=wps_connection_name)
            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.SNOWFLAKE)
            assert wps_connection.metadata == {}
        finally:
            client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.SNOWFLAKE))

    def test_workspace_connections_create_update_and_delete_s3_access_key(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(source="./tests/test_configs/connection/s3_access_key.yaml")

        wps_connection.name = wps_connection_name

        try:
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.ACCESS_KEY)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.S3)
            assert wps_connection.metadata == {}

            wps_connection.credentials.access_key_id = "dummy"
            wps_connection.credentials.secret_access_key = "dummy"
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.ACCESS_KEY)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.S3)

            wps_connection = client.connections.get(name=wps_connection_name)
            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.ACCESS_KEY)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.S3)
            assert wps_connection.metadata == {}
        finally:
            client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_content_safety(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(source="./tests/test_configs/connection/content_safety_with_key.yaml")
        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)
        client.connections.delete(name=wps_connection_name)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert wps_connection.type == ConnectionTypes.AZURE_CONTENT_SAFETY
        assert wps_connection.metadata is not None

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_speech(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(source="./tests/test_configs/connection/speech_with_key.yaml")
        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)
        client.connections.delete(name=wps_connection_name)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert wps_connection.type == ConnectionTypes.AZURE_SPEECH_SERVICES
        assert wps_connection.metadata is not None

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_ai_search(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(source="./tests/test_configs/connection/search_with_key.yaml")
        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)
        client.connections.delete(name=wps_connection_name)

        assert type(wps_connection) == AzureAISearchConnection
        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        # assert wps_connection.api_key == "3333" # TODO add api key retrieval everywhere
        assert wps_connection.type == ConnectionTypes.AZURE_SEARCH
        assert wps_connection.metadata is not None

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    # Involved test, takes 5+ minutes to run in live mode.
    # Makes use of a lot of hub and lean workspace creation, so changes to those can cause this test to fail.
    @pytest.mark.shareTest
    @pytest.mark.skipif(condition=True, reason="Resource creation API result inconsistent in uncontrollable way.")
    def test_workspace_connection_is_shared_behavior(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Create a workspace hub and 2 child lean workspaces
        hub = client.workspaces.begin_create(workspace=Hub(name=f"e2etest_{randstr('hub_name')}")).result()
        poller1 = client.workspaces.begin_create(
            workspace=Workspace(name=f"e2etest_{randstr('lean_ws1')}", workspace_hub=hub.id)
        )
        lean_ws1 = poller1.result()
        # Lean workspaces can't be created in parallel sadly. Doing so risks parallel operation conflict errors.
        poller2 = client.workspaces.begin_create(
            workspace=Workspace(name=f"e2etest_{randstr('lean_ws2')}", workspace_hub=hub.id)
        )
        lean_ws2 = poller2.result()

        # Create clients for the three workspaces
        hub_client = MLClient(
            credential=client._credential,
            subscription_id=client.subscription_id,
            resource_group_name=client.resource_group_name,
            workspace_name=hub.name,
        )
        lean_client1 = MLClient(
            credential=client._credential,
            subscription_id=client.subscription_id,
            resource_group_name=client.resource_group_name,
            workspace_name=lean_ws1.name,
        )
        lean_client2 = MLClient(
            credential=client._credential,
            subscription_id=client.subscription_id,
            resource_group_name=client.resource_group_name,
            workspace_name=lean_ws2.name,
        )

        # Create 4 connections, 2 in the hub, and 2 in one of the lean workspaces, toggling
        # the "is_shared" property.
        # Names don't need randomization since the containers are transient
        hub_conn_shared = WorkspaceConnection(
            name="sharedHubConn",
            type=ConnectionTypes.CUSTOM,
            target="notReal",
            credentials=ApiKeyConfiguration(key="1111"),
        )
        # Hubs can't actually have is_shared be false, make sure this is overridden upon creation.
        hub_conn_closed = WorkspaceConnection(
            name="closedHubConn",
            type=ConnectionTypes.CUSTOM,
            target="notReal",
            credentials=ApiKeyConfiguration(key="2222"),
            is_shared=False,
        )
        lean_conn_shared = WorkspaceConnection(
            name="sharedLeanConn",
            type=ConnectionTypes.CUSTOM,
            target="notReal",
            credentials=ApiKeyConfiguration(key="3333"),
        )
        lean_conn_closed = WorkspaceConnection(
            name="closedLeanConn",
            type=ConnectionTypes.CUSTOM,
            target="notReal",
            credentials=ApiKeyConfiguration(key="4444"),
            is_shared=False,
        )
        hub_conn_shared = hub_client.connections.create_or_update(workspace_connection=hub_conn_shared)
        assert hub_conn_shared.is_shared

        hub_conn_closed = hub_client.connections.create_or_update(workspace_connection=hub_conn_closed)
        # Expected, hubs can't have is_shared==False.
        assert hub_conn_closed.is_shared

        lean_conn_shared = lean_client1.connections.create_or_update(workspace_connection=lean_conn_shared)
        assert lean_conn_shared.is_shared

        lean_conn_closed = lean_client1.connections.create_or_update(workspace_connection=lean_conn_closed)
        assert not lean_conn_closed.is_shared

        # Since the two hub connections are functionally identical, test permutations of 3
        # connections and clients for expected behavior.
        assert hub_client.connections.get(name=hub_conn_shared.name) is not None
        assert lean_client1.connections.get(name=hub_conn_shared.name) is not None
        assert lean_client2.connections.get(name=hub_conn_shared.name) is not None

        assert hub_client.connections.get(name=lean_conn_shared.name) is not None
        assert lean_client1.connections.get(name=lean_conn_shared.name) is not None
        assert lean_client2.connections.get(name=lean_conn_shared.name) is not None

        assert hub_client.connections.get(name=lean_conn_closed.name) is not None
        assert lean_client1.connections.get(name=lean_conn_closed.name) is not None
        # This is the only case we expect to fail. Lean workspace 2 cannot access the
        # un-shared connection from lean workspace 1.
        with pytest.raises(ResourceNotFoundError, match="Connection closedLeanConn can't be found in this workspace"):
            lean_client2.connections.get(name=lean_conn_closed.name)

        # We expect 6/5 connections instead of 4/3 because of the 2 default connections that are created
        # for ai resources.
        assert len([x for x in hub_client.connections.list()]) == 6
        assert len([x for x in lean_client1.connections.list()]) == 6
        assert len([x for x in lean_client2.connections.list()]) == 5

        # Lean workspaces need to be fully deleted before parent hub can be deleted.
        del_lean1 = client.workspaces.begin_delete(name=lean_ws1.name, delete_dependent_resources=False)
        del_lean2 = client.workspaces.begin_delete(name=lean_ws2.name, delete_dependent_resources=False)
        del_lean1.result()
        del_lean2.result()
        client.workspace_hubs.begin_delete(name=hub.name, delete_dependent_resources=True)

    @pytest.mark.shareTest
    @pytest.mark.skipif(condition=True, reason="Backend behavior this test relies on has shifted. Need to refactor.")
    def test_workspace_connection_data_connection_listing(
        self,
        client: MLClient,
        randstr: Callable[[], str],
        account_keys: Tuple[str, str],
        blob_store_file: str,
        storage_account_name: str,
    ) -> None:
        # Connections cannot be used to CREATE datastore connections, so we need
        # to use normal datastore operations to first make a blob datastore that we can
        # then use to test against the data connection listing functionality.
        # This test borrows heavily from the datastore e2e tests.

        # Create a blob datastore.
        primary_account_key, secondary_account_key = account_keys
        random_name = randstr("random_name")
        params_override = [
            {"credentials.account_key": primary_account_key},
            {"name": random_name},
            {"account_name": storage_account_name},
        ]
        internal_blob_ds = load_datastore(blob_store_file, params_override=params_override)

        created_datastore = None
        created_connection = None
        try:
            created_datastore = self.datastore_create_get_list(client, internal_blob_ds, random_name)
            assert isinstance(created_datastore, AzureBlobDatastore)
            assert created_datastore.container_name == internal_blob_ds.container_name
            assert created_datastore.account_name == internal_blob_ds.account_name
            assert created_datastore.credentials.account_key == primary_account_key

            # Now that a datastore exists, create a connection to it
            local_connection = AzureBlobStoreConnection(
                name=created_datastore.name,
                url=created_datastore.base_path,
                account_name=created_datastore.account_name,
                container_name=created_datastore.container_name,
                credentials=AccountKeyConfiguration(account_key=created_datastore.credentials.account_key),
            )

            created_connection = client.connections.create_or_update(workspace_connection=local_connection)

            # Make sure that normal list call doesn't include data connection
            assert internal_blob_ds.name not in [conn.name for conn in client.connections.list()]

            # Make sure that the data connection list call includes the data connection
            found_datastore_conn = False
            for conn in client.connections.list(include_data_connections=True):
                if created_datastore.name == conn.name:
                    assert conn.type == camel_to_snake(ConnectionCategory.AZURE_BLOB)
                    assert isinstance(conn, AzureBlobStoreConnection)
                    found_datastore_conn = True
            # Ensure that we actually found and validated the data connection.
            assert found_datastore_conn
        finally:
            # Delete resources
            if created_connection is not None:
                client.connections.delete(name=created_datastore.name)
            if created_datastore is not None:
                client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)

    # Helper function copied from datstore e2e test.
    def datastore_create_get_list(self, client: MLClient, datastore: Datastore, random_name: str) -> Datastore:
        client.datastores.create_or_update(datastore)
        datastore = client.datastores.get(random_name, include_secrets=True)
        assert datastore.name == random_name
        ds_list = client.datastores.list()
        assert any(ds.name == datastore.name for ds in ds_list)
        return datastore

    # New generation WC subclass tests (new as of april 2024)

    def test_alds_gen_2_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name1')}"
        local_connection = load_connection(source="./tests/test_configs/connection/alds_gen2_sp.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, WorkspaceConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.type == ConnectionTypes.AZURE_DATA_LAKE_GEN_2
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.SERVICE_PRINCIPAL)
        assert created_connection.metadata["four"] == "five"
        assert created_connection.target == "my_endpoint"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name2')}"
        local_connection = load_connection(source="./tests/test_configs/connection/alds_gen2_entra.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, WorkspaceConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.type == ConnectionTypes.AZURE_DATA_LAKE_GEN_2
        assert created_connection.credentials.type == ConnectionAuthType.AAD.lower()
        assert created_connection.metadata["four"] == "five"
        assert created_connection.target == "my_endpoint"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_one_lake_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name1')}"
        local_connection = load_connection(source="./tests/test_configs/connection/one_lake_with_name.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, MicrosoftOneLakeConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.type == camel_to_snake(ConnectionCategory.AZURE_ONE_LAKE)
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.SERVICE_PRINCIPAL)
        assert created_connection.target == "https://www.endpoint.com/the_workspace_name/my_lake_name.Lakehouse"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name2')}"
        local_connection = load_connection(source="./tests/test_configs/connection/one_lake_with_id.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)
        assert isinstance(created_connection, MicrosoftOneLakeConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.type == camel_to_snake(ConnectionCategory.AZURE_ONE_LAKE)
        assert created_connection.credentials.type == ConnectionAuthType.AAD.lower()
        assert (
            created_connection.target
            == "https://www.endpoint.com/the_workspace_name/1234567-1234-1234-1234-123456789012"
        )

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_azure_open_ai_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name1')}"
        local_connection = load_connection(source="./tests/test_configs/connection/azure_open_ai_api.yaml")
        local_connection.name = wps_connection_name
        local_connection.open_ai_resource_id = None  # Not dealing with finding a valid ID for this test
        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureOpenAIConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == camel_to_snake(ConnectionCategory.AZURE_OPEN_AI)
        expected_key = "12344" if is_live() else "dGhpcyBpcyBmYWtlIGtleQ=="
        assert created_connection.api_key == expected_key
        assert created_connection.metadata is not None
        assert created_connection.metadata["hello"] == "world"
        assert created_connection.api_version == "1.0"
        assert created_connection.open_ai_resource_id == None

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name2')}"
        local_connection = load_connection(source="./tests/test_configs/connection/azure_open_ai_entra.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureOpenAIConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == ConnectionAuthType.AAD.lower()
        assert created_connection.type == camel_to_snake(ConnectionCategory.AZURE_OPEN_AI)
        assert created_connection.metadata is not None
        assert created_connection.metadata["hello"] == "world"
        assert created_connection.api_version is None
        assert created_connection.open_ai_resource_id == None

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    @pytest.mark.skipif(
        condition=True,
        reason="Backend validation requires valid input data, which I don't want to surface here, or learn to scrub from a recording.",
    )
    def test_azure_ai_services_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name1')}"
        local_connection = load_connection(source="./tests/test_configs/connection/ai_services_with_key.yaml")
        local_connection.name = wps_connection_name
        # local_connection._target = "https://<ai-services-name>.cognitiveservices.azure.com/"
        # local_connection.ai_services_resource_id = "/subscriptions/<sub-id>/resourceGroups/<rg-name>/providers/Microsoft.CognitiveServices/accounts/<ai-services name>"
        # local_connection.api_key ="<valid-key>"
        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)
        assert isinstance(created_connection, AzureAIServicesConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == ConnectionTypes.AZURE_AI_SERVICES

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name2')}"
        local_connection = load_connection(source="./tests/test_configs/connection/ai_services_with_entra.yaml")
        local_connection.name = wps_connection_name
        # Need similar value injection as before
        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureAIServicesConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == ConnectionAuthType.AAD.lower()
        assert created_connection.type == ConnectionTypes.AZURE_AI_SERVICES

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_content_safety_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name1')}"
        local_connection = load_connection(source="./tests/test_configs/connection/content_safety_with_key.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureContentSafetyConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == ConnectionTypes.AZURE_CONTENT_SAFETY
        assert created_connection.target == "my_endpoint"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name2')}"
        local_connection = load_connection(source="./tests/test_configs/connection/content_safety_with_entra.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureContentSafetyConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == ConnectionAuthType.AAD.lower()
        assert created_connection.type == ConnectionTypes.AZURE_CONTENT_SAFETY
        assert created_connection.target == "my_endpoint"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_speech_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name1')}"
        local_connection = load_connection(source="./tests/test_configs/connection/speech_with_key.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureSpeechServicesConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == ConnectionTypes.AZURE_SPEECH_SERVICES
        assert created_connection.target == "my_endpoint"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name2')}"
        local_connection = load_connection(source="./tests/test_configs/connection/speech_with_entra.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureSpeechServicesConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == ConnectionAuthType.AAD.lower()
        assert created_connection.type == ConnectionTypes.AZURE_SPEECH_SERVICES
        assert created_connection.target == "my_endpoint"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_search_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name1')}"
        local_connection = load_connection(source="./tests/test_configs/connection/search_with_key.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureAISearchConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == ConnectionTypes.AZURE_SEARCH
        assert created_connection.target == "this_is_a_target"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_conn_name2')}"
        local_connection = load_connection(source="./tests/test_configs/connection/search_with_entra.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(
            workspace_connection=local_connection, populate_secrets=True
        )
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, AzureAISearchConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == ConnectionAuthType.AAD.lower()
        assert created_connection.type == ConnectionTypes.AZURE_SEARCH
        assert created_connection.target == "this_is_a_target_too"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_generic_api_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        local_connection = load_connection(source="./tests/test_configs/connection/api_key_conn.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, APIKeyConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == camel_to_snake(ConnectionCategory.API_KEY)
        assert created_connection.target == "this_is_a_target"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_custom_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"
        local_connection = load_connection(source="./tests/test_configs/connection/custom.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, WorkspaceConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == camel_to_snake(ConnectionTypes.CUSTOM)
        assert created_connection.metadata is not None
        assert created_connection.is_shared

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_non_azure_open_ai_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        local_connection = load_connection(source="./tests/test_configs/connection/not_azure_open_ai.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, OpenAIConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == camel_to_snake(ConnectionCategory.OPEN_AI)
        assert created_connection.target is None

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_serp_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        local_connection = load_connection(source="./tests/test_configs/connection/serp.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, SerpConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == camel_to_snake(ConnectionCategory.SERP)
        assert created_connection.target is None

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_git_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        local_connection = load_connection(source="./tests/test_configs/connection/git_no_cred.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, WorkspaceConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == ConnectionAuthType.NONE
        assert created_connection.type == camel_to_snake(ConnectionCategory.GIT)
        assert created_connection.target == "https://test-git-feed.com2"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_python_feed_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(source="./tests/test_configs/connection/python_feed_pat.yaml")

        wps_connection.name = wps_connection_name

        try:
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
            assert wps_connection.metadata == {}
            # TODO : Uncomment once service side returns creds correctly
            # assert wps_connection.credentials.pat == "dummy_pat"

            wps_connection.credentials.pat = "dummpy_pat_update"
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)

            wps_connection = client.connections.get(name=wps_connection_name)
            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
            assert wps_connection.metadata == {}
            # TODO : Uncomment once service side returns creds correctly
            # assert wps_connection.credentials.pat == "dummpy_pat_update"
        finally:
            client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_container_registry_managed_id_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_connection(
            source="./tests/test_configs/connection/container_registry_managed_identity.yaml"
        )

        wps_connection.name = wps_connection_name
        try:
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.MANAGED_IDENTITY)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY)
            assert wps_connection.metadata == {}
            # TODO : Uncomment once service side returns creds correctly
            # assert wps_connection.credentials.pat == "dummy_pat"

            wps_connection.credentials.client_id = "dummpy_client_id"
            wps_connection.credentials.resource_id = "dummpy_resource_id"
            wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.MANAGED_IDENTITY)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY)

            wps_connection = client.connections.get(name=wps_connection_name)
            assert wps_connection.name == wps_connection_name
            assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.MANAGED_IDENTITY)
            assert wps_connection.type == camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY)
            # TODO : Uncomment once service side returns creds correctly
            # assert wps_connection.credentials.pat == "dummpy_pat_update"
        finally:
            client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_serverless_crud(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        local_connection = load_connection(source="./tests/test_configs/connection/serverless_api.yaml")
        local_connection.name = wps_connection_name

        created_connection = client.connections.create_or_update(workspace_connection=local_connection)
        client.connections.delete(name=wps_connection_name)

        assert isinstance(created_connection, ServerlessConnection)
        assert created_connection.name == wps_connection_name
        assert created_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert created_connection.type == camel_to_snake(ConnectionCategory.SERVERLESS)
        assert created_connection.target == "serverless_endpoint"

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)
