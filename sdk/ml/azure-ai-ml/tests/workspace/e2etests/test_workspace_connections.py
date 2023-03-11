# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_workspace_connection
from azure.ai.ml._restclient.v2022_01_01_preview.models import ConnectionAuthType, ConnectionCategory
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import WorkspaceConnection


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
        assert wps_connection.metadata is None
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
        assert wps_connection.metadata is None
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummpy_pat_update"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.PYTHON_FEED))

        for conn in connection_list:
            print(conn)

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
        assert wps_connection.metadata is None
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummpy_pat_update"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.GIT))

        for conn in connection_list:
            print(conn)

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
        assert wps_connection.metadata is None
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
        assert wps_connection.metadata is None
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummpy_pat_update"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY))

        for conn in connection_list:
            print(conn)

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
        assert wps_connection.metadata is None
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
        assert wps_connection.metadata is None
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummpy_pat_update"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.GIT))

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="bugged test")
    def test_workspace_connections_create_update_and_delete_featurestore_service_principal(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(
            source="./tests/test_configs/workspace_connection/fs_service_principal.yaml"
        )
        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.target == "azureml://featurestores/featurestore"
        assert wps_connection.credentials.type == ConnectionAuthType.SERVICE_PRINCIPAL
        assert wps_connection.type == ConnectionCategory.FEATURE_STORE
        assert wps_connection.metadata["name"] == "featurestore"
        assert wps_connection.metadata["description"] == "my featurestore"
        assert wps_connection.metadata["type"] == "feast"
        assert wps_connection.metadata["featurestore_config"]
        assert wps_connection.metadata["connection_config"]
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummy_pat"

        wps_connection.target == "azureml://featurestores/featurestore_update"
        wps_connection.credentials.client_id = "client_id_update"
        wps_connection.credentials.client_secret = "PasswordPlaceHolder_Update"
        wps_connection.credentials.tenant_id = "tenant_id_update"
        wps_connection.metadata["name"] == "featurestore_update"
        wps_connection.metadata["description"] == "my featurestore update"
        wps_connection.metadata["type"] == "azure_feature_store"
        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.target == "azureml://featurestores/featurestore_update"
        assert wps_connection.credentials.type == ConnectionAuthType.SERVICE_PRINCIPAL
        assert wps_connection.type == ConnectionCategory.FEATURE_STORE

        wps_connection = client.connections.get(name=wps_connection_name)
        assert wps_connection.name == wps_connection_name
        assert wps_connection.target == "azureml://featurestores/featurestore_update"
        assert wps_connection.credentials.type == ConnectionAuthType.SERVICE_PRINCIPAL
        assert wps_connection.type == ConnectionCategory.FEATURE_STORE
        assert wps_connection.credentials
        assert wps_connection.metadata["name"] == "featurestore_update"
        assert wps_connection.metadata["description"] == "my featurestore update"
        assert wps_connection.metadata["type"] == "azure_feature_store"
        assert wps_connection.metadata["featurestore_config"]
        assert wps_connection.metadata["connection_config"]
        # TODO : Uncomment once service side returns creds correctly
        # assert wps_connection.credentials.pat == "dummpy_pat_update"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=ConnectionCategory.FEATURE_STORE)

        for conn in connection_list:
            print(conn)

    def test_workspace_connections_create_update_and_delete_snowflake_user_pwd(
        self,
        client: MLClient,
        randstr: Callable[[], str],
    ) -> None:
        wps_connection_name = f"e2etest_wps_conn_{randstr('wps_connection_name')}"

        wps_connection = load_workspace_connection(source="./tests/test_configs/workspace_connection/snowflake_user_pwd.yaml")

        wps_connection.name = wps_connection_name

        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.SNOWFLAKE)
        assert wps_connection.metadata is None

        wps_connection.credentials.username = "dummpy_u"
        wps_connection.credentials.password = "dummpy_p"
        wps_connection = client.connections.create_or_update(workspace_connection=wps_connection)

        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.SNOWFLAKE)

        wps_connection = client.connections.get(name=wps_connection_name)
        assert wps_connection.name == wps_connection_name
        assert wps_connection.credentials.type == camel_to_snake(ConnectionAuthType.USERNAME_PASSWORD)
        assert wps_connection.type == camel_to_snake(ConnectionCategory.SNOWFLAKE)
        assert wps_connection.metadata is None

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.SNOWFLAKE))

        for conn in connection_list:
            print(conn)
