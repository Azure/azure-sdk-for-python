from typing import Callable
import pytest

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities import AIResource
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import  is_live
# NOTE: Expect 2 AI Projects to exist already in the provided AI Client's resource group:
# e2e_test_res_1 and e2e_test_res_2. Furthermore, the former is expected
# to be the client's default AI resource

@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestResources:
    def test_resource_get_and_list(self, ai_client: AIClient):
        expected_resources = ["e2e_test_res_1", "e2e_test_res_2"]
        resources = ai_client.ai_resources.list()
        assert len(resources) >= len(expected_resources)
        expected_count = 0
        for listed_resource in resources:
            name = listed_resource.name

            if name in expected_resources:
                expected_count += 1
                gotten_resource = ai_client.ai_resources.get(name=name)
                assert gotten_resource.name == name

        assert expected_count == len(expected_resources)

    # DEV NOTE: due to how long it takes for 3 LROPollers to resolve, this test can easily take a couple minutes to run in live mode
    @pytest.mark.skipif(condition=not is_live(), reason="Random generation in ARM template(?) makes create recordings useless.")
    def test_create_update_and_delete(self, ai_client: AIClient, rand_num: Callable[[], str]):
        new_local_resource = AIResource(
            name="test_resource_" + rand_num(),
            description="Transient test object. Delete if seen.",
            resource_group=ai_client.resource_group_name,
            default_project_resource_group=f"/subscriptions/{ai_client.subscription_id}/resourceGroups/{ai_client.resource_group_name}",
        )
        created_poller = ai_client.ai_resources.begin_create(ai_resource=new_local_resource)
        created_resource = created_poller.result()
        assert new_local_resource.name == created_resource.name
        assert new_local_resource.description == created_resource.description
        assert new_local_resource.default_project_resource_group == new_local_resource.default_project_resource_group

        delete_poller = ai_client.ai_resources.begin_delete(
            name=new_local_resource.name, delete_dependent_resources=True
        )
        delete_poller.wait()
        with pytest.raises(ResourceNotFoundError):
            ai_client.ai_resources.get(name=new_local_resource.name)
