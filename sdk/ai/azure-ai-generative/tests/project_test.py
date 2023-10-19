import pytest

from azure.ai.generative import AIClient
from azure.ai.generative.entities import Project
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
class TestProjects:
    def test_get_and_list(self, ai_client: AIClient):
        expected_projects = ["e2e_test_lean_project_1", "e2e_test_lean_project_2"]
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
    def test_create_update_and_delete(self, ai_client: AIClient):
        new_local_project = Project(
            name="e2e_test_created_project",
            ai_resource="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/hanchi-test/providers/Microsoft.MachineLearningServices/workspaces/e2e_test_resource_1",
            description="A project made during the generative SDK's e2e test suite. Should be deleted shortly.",
            display_name="transient_project",
        )
        create_poller = ai_client.projects.begin_create(project=new_local_project)
        created_project = create_poller.result()
        assert created_project.name == new_local_project.name
        assert created_project.ai_resource == new_local_project.ai_resource
        assert created_project.display_name == new_local_project.display_name

        new_local_project.display_name = "updated_project_name"
        update_poller = ai_client.projects.begin_update(project=new_local_project)
        updated_project = update_poller.result()

        assert new_local_project.display_name == updated_project.display_name

        delete_poller = ai_client.projects.begin_delete(name=new_local_project.name, delete_dependent_resources=True)
        delete_poller.wait()

        with pytest.raises(ResourceNotFoundError):
            ai_client.projects.get(name=new_local_project.name)
