# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable, Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_workspace_connection, load_datastore
from azure.ai.ml._restclient.v2024_01_01_preview.models import ConnectionAuthType, ConnectionCategory
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import (
    WorkspaceConnection,
    Workspace,
    WorkspaceHub,
    ApiKeyConfiguration,
    AzureBlobDatastore,
    AzureBlobStoreWorkspaceConnection,
)
from azure.ai.ml.constants._common import WorkspaceConnectionTypes
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml.entities._datastore.datastore import Datastore


@pytest.mark.xdist_group(name="workspace_connection")
@pytest.mark.e2etest
@pytest.mark.core_sdk_test
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceConnections(AzureRecordedTestCase):
    def test_workspace_connections_create_update_and_delete_python_feed(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(
            source="./tests/test_configs/workspace_connection/python_feed_pat.yaml"
        )

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
        assert wps_connection.tags == {}
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
        assert wps_connection.tags == {}
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummpy_pat_update"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_git_pat(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(source="./tests/test_configs/workspace_connection/git_pat.yaml")

        wps_connection.name = wps_connection_name

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
        assert wps_connection.tags == {}
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummpy_pat_update"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_cr_msi(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(
            source="./tests/test_configs/workspace_connection/container_registry_managed_identity.yaml"
        )

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.MANAGED_IDENTITY)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY)
        assert wps_connection.tags == {}
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

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_git_user_pwd(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(source="./tests/test_configs/workspace_connection/git_user_pwd.yaml")

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.GIT)
        assert wps_connection.tags == {}
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummy_pat"

        wps_connection.credentials.username = "dummpy_u"
        wps_connection.credentials.password = "dummpy_p"
        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.GIT)

        wps_connection = client.connections.get(name=wps_connection_name)
        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.GIT)
        assert wps_connection.tags == {}
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummpy_pat_update"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.GIT))

    def test_workspace_connections_create_update_and_delete_snowflake_user_pwd(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(
            source="./tests/test_configs/workspace_connection/snowflake_user_pwd.yaml"
        )

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.SNOWFLAKE)
        assert wps_connection.tags == {}

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
        assert wps_connection.tags == {}

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

        wps_connection = load_workspace_connection(
            source="./tests/test_configs/workspace_connection/s3_access_key.yaml"
        )

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.ACCESS_KEY)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.S3)
        assert wps_connection.tags == {}

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
        assert wps_connection.tags == {}

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_open_ai_conn(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(source="./tests/test_configs/workspace_connection/open_ai.yaml")

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.AZURE_OPEN_AI)
        assert wps_connection.tags is not None
        assert wps_connection.tags["hello"] == "world"
        assert wps_connection.api_type == "Azure"
        assert wps_connection.api_version == None

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_cog_search_conn(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(source="./tests/test_configs/workspace_connection/cog_search.yaml")

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.COGNITIVE_SEARCH)
        assert wps_connection.tags is not None
        assert wps_connection.api_version == "dummy"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_cog_service_conn(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(source="./tests/test_configs/workspace_connection/cog_service.yaml")

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.COGNITIVE_SERVICE)
        assert wps_connection.tags is not None
        assert wps_connection.api_version == "dummy"
        assert wps_connection.kind == "some_kind"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    def test_workspace_connections_create_update_and_delete_custom_conn(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(source="./tests/test_configs/workspace_connection/custom.yaml")

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert wps_connection.type == camel_to_snake(WorkspaceConnectionTypes.CUSTOM)
        assert wps_connection.tags is not None
        assert wps_connection.is_shared

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

    # Involved test, takes 5+ minutes to run in live mode.
    # Makes use of a lot of hub and lean workspace creation, so changes to those can cause this test to fail.
    @pytest.mark.shareTest
    @pytest.mark.skipif(condition=True, reason="Resource creation API result inconsistent in uncontrollable way.")
    def test_workspace_connection_is_shared_behavior(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Create a workspace hub and 2 child lean workspaces
        hub = client.workspace_hubs.begin_create(
            workspace_hub=WorkspaceHub(name=f"e2etest_{randstr('hub_name')}")
        ).result()
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
            type=WorkspaceConnectionTypes.CUSTOM,
            target="notReal",
            credentials=ApiKeyConfiguration(key="1111"),
        )
        # Hubs can't actually have is_shared be false, make sure this is overridden upon creation.
        hub_conn_closed = WorkspaceConnection(
            name="closedHubConn",
            type=WorkspaceConnectionTypes.CUSTOM,
            target="notReal",
            credentials=ApiKeyConfiguration(key="2222"),
            is_shared=False,
        )
        lean_conn_shared = WorkspaceConnection(
            name="sharedLeanConn",
            type=WorkspaceConnectionTypes.CUSTOM,
            target="notReal",
            credentials=ApiKeyConfiguration(key="3333"),
        )
        lean_conn_closed = WorkspaceConnection(
            name="closedLeanConn",
            type=WorkspaceConnectionTypes.CUSTOM,
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
    def test_workspace_connection_data_connection_listing(
        self,
        client: MLClient,
        randstr: Callable[[], str],
        account_keys: Tuple[str, str],
        blob_store_file: str,
        storage_account_name: str,
    ) -> None:
        # Workspace connections cannot be used to CREATE datastore connections, so we need
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
        created_datastore = datastore_create_get_list(client, internal_blob_ds, random_name)
        assert isinstance(created_datastore, AzureBlobDatastore)
        assert created_datastore.container_name == internal_blob_ds.container_name
        assert created_datastore.account_name == internal_blob_ds.account_name
        assert created_datastore.credentials.account_key == primary_account_key

        # Make sure that normal list call doesn't include data connection
        assert internal_blob_ds.name not in [conn.name for conn in client.connections.list()]

        # Make sure that the data connection list call includes the data connection
        found_datastore_conn = False
        for conn in client.connections.list(include_data_connections=True):
            if created_datastore.name == conn.name:
                assert conn.type == camel_to_snake(ConnectionCategory.AZURE_BLOB)
                assert isinstance(conn, AzureBlobStoreWorkspaceConnection)
                found_datastore_conn = True
        # Ensure that we actually found and validated the data connection.
        assert found_datastore_conn
        # delete the data store.
        client.datastores.delete(random_name)
        with pytest.raises(Exception):
            client.datastores.get(random_name)


# Helper function copied from datstore e2e test.
def datastore_create_get_list(client: MLClient, datastore: Datastore, random_name: str) -> Datastore:
    client.datastores.create_or_update(datastore)
    datastore = client.datastores.get(random_name, include_secrets=True)
    assert datastore.name == random_name
    ds_list = client.datastores.list()
    assert any(ds.name == datastore.name for ds in ds_list)
    return datastore
