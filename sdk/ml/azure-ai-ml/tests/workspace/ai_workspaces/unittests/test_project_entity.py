import pytest

from azure.ai.ml import load_workspace
from azure.ai.ml.entities import Project


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestProjectEntity:
    def test_project_schema_manipulation(self) -> None:
        project = load_workspace(source="./tests/test_configs/workspace/ai_workspaces/test_project.yml")

        assert project is not None
        assert type(project) == Project
        assert project.name == "test_project"
        assert project.description == "A test project for unit tests"
        assert (
            project.location
            == "this must match the parent's hub (unless we want to add the ability for projects to derive the hubs parent with an extra API call)"
        )
        assert project.resource_group == "my-test-rg-which-can-be-different-from-the-hubs-rg"
        assert project.tags == {"extra_data": "some value"}
        assert (
            project.hub_id
            == "/subscriptions/abc-123-drm-abc/resourceGroups/my-test-rg/providers/Microsoft.MachineLearningServices/workspaces/my-test-hub"
        )
