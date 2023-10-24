# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_workspace_connection
from azure.ai.ml._restclient.v2023_06_01_preview.models import ConnectionAuthType, ConnectionCategory
from azure.ai.ml._utils.utils import camel_to_snake


@pytest.mark.xdist_group(name="workspace_connection")
@pytest.mark.e2etest
@pytest.mark.core_sdk_test
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceConnections(AzureRecordedTestCase):
    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.PYTHON_FEED))

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.GIT))

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY))

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.S3))

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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
        assert wps_connection.api_type == "some_type"
        assert wps_connection.api_version == "some_version"

        client.connections.delete(name=wps_connection_name)

        with pytest.raises(Exception):
            client.connections.get(name=wps_connection_name)

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.S3))

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.S3))

        for conn in connection_list:
            print(conn)

    @pytest.mark.skip(reason="TODO: Message: e2e recording not working")
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

        connection_list = client.connections.list(connection_type=camel_to_snake(ConnectionCategory.S3))

        for conn in connection_list:
            print(conn)
