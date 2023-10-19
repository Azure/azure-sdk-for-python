import pytest

from azure.ai.generative import AIClient
from azure.ai.generative.entities import AIResource
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
class TestResources:
    def test_get_and_list(self, ai_client: AIClient):
        expected_resources = ["e2e_test_resource_1", "e2e_test_resource_2"]
        resources = ai_client.ai_resources.list()
        assert len(resources) >= len(expected_resources)
        expected_count = 0
        for listed_resource in resources:
            name = listed_resource.name

            if name in expected_resources:
                expected_count += 1
                gotten_resource = ai_client.ai_resources.get(name=name)
                assert gotten_resource.name == name
                # TODO other stuff to match between them

        assert expected_count == len(expected_resources)

    # DEV NOTE: due to how long it takes for 3 LROPollers to resolve, this test can easily take a couple minutes to run in live mode
    def test_create_update_and_delete(self, ai_client: AIClient):
        new_local_resource = AIResource(
            name="e2e_test_created_resource",
            description="A transient resource/workspace hub created by the generative SDK e2e test for resources. Should be deleted shortly.",
            resource_group=ai_client.resource_group_name,
        )
        created_poller = ai_client.ai_resources.begin_create(ai_resource=new_local_resource)
        created_resource = created_poller.result()
        assert new_local_resource.name == created_resource.name
        assert new_local_resource.description == created_resource.description

        new_local_resource.description = "e2e test: updated description"
        updated_poller = ai_client.ai_resources.begin_update(ai_resource=new_local_resource)
        updated_resource = updated_poller.result()
        assert new_local_resource.name == updated_resource.name
        assert updated_resource.description == "e2e test: updated description"

        delete_poller = ai_client.ai_resources.begin_delete(
            name=new_local_resource.name, delete_dependent_resources=True
        )
        delete_poller.wait()
        with pytest.raises(ResourceNotFoundError):
            ai_client.ai_resources.get(name=new_local_resource.name)
