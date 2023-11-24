from typing import Callable
import pytest

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities import Project
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import  is_live

# Makes the following setup assumptions:
# 2 projects already exist in the conftest's ai_client:
# e2e_test_proj_1 and e2e_test_proj_2.
# The former is the client's default project.

@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestProjects:
    def test_project_get_and_list(self, ai_client: AIClient):
        expected_projects = ["e2e_test_proj_1", "e2e_test_proj_2"]
        projects = ai_client.projects.list()
        assert len(projects) >= len(expected_projects)

        expected_count = 0
        for listed_project in projects:
            name = listed_project.name

            if name in expected_projects:
                expected_count += 1
                gotten_project = ai_client.projects.get(name=name)
                assert gotten_project.name == name
                # TODO other stuff to match between them
        assert expected_count == len(expected_projects)

    # DEV NOTE: due to how long it takes for 3 LROPollers to resolve, this test can easily take a couple minutes to run in live mode
    @pytest.mark.skipif(condition=not is_live(), reason="Random generation in ARM template(?) makes create recordings useless.")
    def test_create_update_and_delete(self, ai_client: AIClient, rand_num: Callable[[], str]):
        new_local_project = Project(
            name="e2eTestProj" + rand_num(),
            ai_resource=f"/subscriptions/{ai_client.subscription_id}/resourceGroups/{ai_client.resource_group_name}"
             + f"/providers/Microsoft.MachineLearningServices/workspaces/{ai_client.ai_resource_name}",
            description="Transient test project. Delete if seen.",
        )
        created_project = ai_client.projects.begin_create(project=new_local_project).result()
        assert created_project.name == new_local_project.name
        assert created_project.ai_resource == new_local_project.ai_resource


        delete_poller = ai_client.projects.begin_delete(name=created_project.name, delete_dependent_resources=True)
        delete_poller.wait()

        with pytest.raises(ResourceNotFoundError):
            ai_client.projects.get(name=created_project.name)

    # This test should be run live as little as possible, since it requires a special client setup that
    # most users don't have locally, and doesn't clean up easily. Because of this, this test shouldn't ever
    # really be run except as a smoke test, and even then requires some extra value injection that we
    # don't want to save in a commit anywhere.
    @pytest.mark.skipif(condition=True, reason="permissions issues require manual value injection and execution.")
    def test_create_with_restricted_access(self, ai_developer_client: AIClient):
        new_local_project = Project(
            name="e2e_test_perm_proj",
            description="Transient test object. Delete if seen.",
            resource_group=ai_developer_client.resource_group_name,
            ai_resource=ai_developer_client.ai_resource_name
        )
        created_project = ai_developer_client.projects.begin_create(project=new_local_project).result()
        assert new_local_project.name == created_project.name
        assert new_local_project.description == created_project.description

        # Delete is not supported by this role, need to delete this outside the test via a cleaning script.