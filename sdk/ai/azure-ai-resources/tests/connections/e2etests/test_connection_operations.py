from typing import Callable
import pytest

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities import (
    AzureOpenAIConnection,
    AzureAISearchConnection,
    AzureAIServiceConnection,
    GitHubConnection,
    CustomConnection,
    AIResource,
    Project
)
from azure.ai.resources.constants import OperationScope
from azure.ai.ml._restclient.v2023_06_01_preview.models import ConnectionAuthType
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.exceptions import ResourceNotFoundError

@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestConnections:
    @pytest.mark.skipif(condition=True, reason="""Updates cannot be done in parallel with v2 SDK.
        "Remove when 1.13.0 v2 sdk release complete and minimum version is upgraded.""")
    @pytest.mark.noCreate
    def test_get_and_list(self, ai_client: AIClient):
        connection_count = 0
        for listed_conn in ai_client.connections.list():
            connection_count = +1
            getted_conn = ai_client.connections.get(listed_conn.name)
            assert listed_conn.name == getted_conn.name
        assert connection_count > 0

    @pytest.mark.skipif(condition=True, reason="""Updates cannot be done in parallel with v2 SDK.
        "Remove when 1.13.0 v2 sdk release complete and minimum version is upgraded.""")
    @pytest.mark.noCreate
    def test_get_default_connections(self, ai_client: AIClient):
        aoai_conn = ai_client.get_default_aoai_connection()
        assert aoai_conn is not None
        
        content_safety_conn = ai_client.get_default_content_safety_connection()
        assert content_safety_conn is not None

    @pytest.mark.skipif(condition=True, reason="""Updates cannot be done in parallel with v2 SDK.
        "Remove when 1.13.0 v2 sdk release complete and minimum version is upgraded.""")
    def test_aoai_create_and_delete(self, ai_client: AIClient, rand_num: Callable[[], str]):
        # randomize name to avoid stale key name collisions
        name = "testAOAIConn" + rand_num()
        cred = ApiKeyConfiguration(key="1234567")
        target = "test-target"

        # create empty conn to test setters
        local_conn = AzureOpenAIConnection(name="overwrite", credentials=None, target="overwrite")

        local_conn.name = name
        local_conn.credentials = cred
        local_conn.target = target

        first_created_conn = ai_client.connections.create_or_update(local_conn)

        assert first_created_conn.name == name
        assert first_created_conn.type == "azure_open_ai"
        assert first_created_conn.target == "test-target"
        assert first_created_conn.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)

        ai_client.connections.get(name)
        ai_client.connections.delete(name)
        with pytest.raises(ResourceNotFoundError):
            ai_client.connections.get(name)

    @pytest.mark.skipif(condition=True, reason="""Updates cannot be done in parallel with v2 SDK.
        "Remove when 1.13.0 v2 sdk release complete and minimum version is upgraded.""")
    def test_search_create_and_delete(self, ai_client: AIClient, rand_num: Callable[[], str]):
        # randomize name to avoid stale key name collisions
        name = "e2eTestSearchConn" + rand_num()
        conn_type = "azure_open_ai"
        cred = ApiKeyConfiguration(key="1234567")
        target = "test-target"

        # create empty conn to test setters
        local_conn = AzureAISearchConnection(name="overwrite", credentials=None, target="overwrite")

        local_conn.name = name
        local_conn.credentials = cred
        local_conn.target = target

        first_created_conn = ai_client.connections.create_or_update(local_conn)

        assert first_created_conn.name == name
        assert first_created_conn.type == "cognitive_search"
        assert first_created_conn.target == "test-target"
        assert first_created_conn.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)

        ai_client.connections.get(name)
        ai_client.connections.delete(name)
        with pytest.raises(ResourceNotFoundError):
            ai_client.connections.get(name)

    @pytest.mark.skipif(condition=True, reason="""Updates cannot be done in parallel with v2 SDK.
        "Remove when 1.13.0 v2 sdk release complete and minimum version is upgraded.""")
    def test_service_create_and_delete(self, ai_client: AIClient, rand_num: Callable[[], str]):
        # randomize name to avoid stale key name collisions
        name = "e2eTestServiceConn" + rand_num()
        cred = ApiKeyConfiguration(key="1234567")
        target = "test-target"
        kind = "ContentSafety"

        # create empty conn to test setters
        local_conn = AzureAIServiceConnection(name="overwrite", credentials=None, target="overwrite", kind="wrong")

        local_conn.name = name
        local_conn.credentials = cred
        local_conn.target = target
        local_conn.kind = kind

        first_created_conn = ai_client.connections.create_or_update(local_conn)

        assert first_created_conn.name == name
        assert first_created_conn.type == "cognitive_service"
        assert first_created_conn.target == "test-target"
        assert first_created_conn.kind == kind
        assert first_created_conn.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)

        ai_client.connections.get(name)
        ai_client.connections.delete(name)
        with pytest.raises(ResourceNotFoundError):
            ai_client.connections.get(name)

    @pytest.mark.skipif(condition=True, reason="""Updates cannot be done in parallel with v2 SDK.
        "Remove when 1.13.0 v2 sdk release complete and minimum version is upgraded.""")
    def test_git_create_and_delete(self, ai_client: AIClient, rand_num: Callable[[], str]):
        # randomize name to avoid stale key name collisions
        name = "e2eTestGitConn" + rand_num()
        cred = ApiKeyConfiguration(key="1234567")
        target = "test-target"

        local_conn = GitHubConnection(name=name, credentials=cred, target=target)
        first_created_conn = ai_client.connections.create_or_update(local_conn)

        assert first_created_conn.name == name
        assert first_created_conn.type == "git"
        assert first_created_conn.target == target
        assert first_created_conn.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)

        ai_client.connections.get(name)
        ai_client.connections.delete(name)
        with pytest.raises(ResourceNotFoundError):
            ai_client.connections.get(name)

    @pytest.mark.skipif(condition=True, reason="""Updates cannot be done in parallel with v2 SDK.
        "Remove when 1.13.0 v2 sdk release complete and minimum version is upgraded.""")
    def test_custom_create_and_delete(self, ai_client: AIClient, rand_num: Callable[[], str]):
        # randomize name to avoid stale key name collisions
        name = "e2eTestCustomConn" + rand_num()
        cred = ApiKeyConfiguration(key="1234567")
        target = "test-target"

        local_conn = CustomConnection(name=name, credentials=cred, target=target)
        first_created_conn = ai_client.connections.create_or_update(local_conn)

        assert first_created_conn.name == name
        assert first_created_conn.type == "custom"
        assert first_created_conn.target == target
        assert first_created_conn.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)

        ai_client.connections.get(name)
        ai_client.connections.delete(name)
        with pytest.raises(ResourceNotFoundError):
            ai_client.connections.get(name)

    # Involved test, takes 5+ minutes to run in live mode.
    # Makes use of a lot of AI resource and Projects, so changes to those can cause this test to fail.
    @pytest.mark.shareTest
    @pytest.mark.skipif(condition=True, reason="Resource creation API result inconsistent in uncontrollable way.")
    def test_is_shared_and_scoping_behavior(self, ai_client: AIClient, rand_num: Callable[[], str]) -> None:
        # Create a AI resource and 2 child projects
        resource = ai_client.ai_resources.begin_create(ai_resource=AIResource(name=f"e2etest_resource_{rand_num()}")).result()
        poller_1 = ai_client.projects.begin_create(project=Project(name=f"e2etest_proj1_{rand_num()}", ai_resource=resource.id))
        proj_1 = poller_1.result()
        # projects can't be created in parallel sadly. Doing so risks parallel operation conflict errors.
        poller_2 = ai_client.projects.begin_create(project=Project(name=f"e2etest_{rand_num()}", ai_resource=resource.id))
        proj_2 = poller_2.result()

        client_1 = AIClient(
            credential=ai_client._credential,
            subscription_id=ai_client.subscription_id,
            resource_group_name=ai_client.resource_group_name,
            project_name=proj_1.name,
            ai_resource_name=resource.name
        )
        client_2 = AIClient(
            credential=ai_client._credential,
            subscription_id=ai_client.subscription_id,
            resource_group_name=ai_client.resource_group_name,
            project_name=proj_2.name,
            ai_resource_name=resource.name
        )

        # Create 4 connections, 2 in the AI Resource, and 2 in one of the projects, toggling
        # the "is_shared" property.
        # Names don't need randomization since the containers are transient
        parent_conn_shared = CustomConnection(
            name="sharedResConn",
            target="notReal",
            credentials=ApiKeyConfiguration(key="1111")
        )
        # AI Resources can't actually have is_shared be false, make sure this is overridden upon creation.
        parent_conn_closed = CustomConnection(
            name="closedResConn",
            target="notReal",
            credentials=ApiKeyConfiguration(key="2222"),
            is_shared=False
        )
        proj_conn_shared = CustomConnection(
            name="sharedProjConn",
            target="notReal",
            credentials=ApiKeyConfiguration(key="3333")
        )
        proj_conn_closed = CustomConnection(
            name="closedProjConn",
            target="notReal",
            credentials=ApiKeyConfiguration(key="4444"),
            is_shared=False
        )
        parent_conn_shared = client_1.connections.create_or_update(connection=parent_conn_shared)
        assert parent_conn_shared.is_shared

        parent_conn_closed = client_1.connections.create_or_update(connection=parent_conn_closed)
        # Expected, ai resources can't have is_shared==False.
        assert parent_conn_closed.is_shared

        proj_conn_shared = client_1.connections.create_or_update(
            connection=proj_conn_shared,
            scope=OperationScope.PROJECT
        )
        assert proj_conn_shared.is_shared

        proj_conn_closed = client_1.connections.create_or_update(
            connection=proj_conn_closed,
            scope=OperationScope.PROJECT
        )
        assert not proj_conn_closed.is_shared

        # Since the two resource connections are functionally identical, test permutations of 3
        # connections and clients for expected behavior.
        assert client_1.connections.get(name=parent_conn_shared.name) is not None
        assert client_2.connections.get(name=parent_conn_shared.name) is not None
        assert client_1.connections.get(name=parent_conn_shared.name, scope=OperationScope.PROJECT) is not None
        assert client_2.connections.get(name=parent_conn_shared.name, scope=OperationScope.PROJECT) is not None
        
        assert client_1.connections.get(name=proj_conn_shared.name) is not None
        assert client_2.connections.get(name=proj_conn_shared.name) is not None
        assert client_1.connections.get(name=proj_conn_shared.name, scope=OperationScope.PROJECT) is not None
        assert client_2.connections.get(name=proj_conn_shared.name, scope=OperationScope.PROJECT) is not None

        assert client_1.connections.get(name=proj_conn_closed.name) is not None
        assert client_2.connections.get(name=proj_conn_closed.name) is not None
        assert client_1.connections.get(name=proj_conn_closed.name, scope=OperationScope.PROJECT) is not None
        # This is the only case we expect to fail. project 2 cannot access the
        # un-shared connection from project 1, when scoped to a project-based search.
        with pytest.raises(ResourceNotFoundError, match=f"Connection {proj_conn_closed.name} can't be found in this workspace"):
            client_2.connections.get(name=proj_conn_closed.name, scope=OperationScope.PROJECT)

        # We expect 6/5 connections instead of 4/3 because of the 2 default connections that are created
        # for ai resources.
        assert len([x for x in client_1.connections.list()]) == 6
        assert len([x for x in client_2.connections.list()]) == 6
        assert len([x for x in client_1.connections.list(scope=OperationScope.PROJECT)]) == 6
        assert len([x for x in client_2.connections.list(scope=OperationScope.PROJECT)]) == 5

        # projects need to be fully deleted before parent resource can be deleted.
        del_1 = client_1.projects.begin_delete(name=proj_1.name, delete_dependent_resources=False)
        del_2 = client_2.projects.begin_delete(name=proj_2.name, delete_dependent_resources=False)
        del_1.result()
        del_2.result()
        client_1.ai_resources.begin_delete(name=resource.name, delete_dependent_resources=True)