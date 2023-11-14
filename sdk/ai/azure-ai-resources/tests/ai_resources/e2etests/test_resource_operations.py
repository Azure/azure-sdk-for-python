import random
import string
import pytest

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities import AIResource
from azure.core.exceptions import ResourceNotFoundError

# NOTE: Expect 2 AI Projects to exist already in the provided AI Client's resource group:
# e2e_test_resource_1 and e2e_test_resource_2. Furthermore, the former is expected
# to be the client's default AI resource

@pytest.mark.e2etest
class TestResources:

    # Code to recreate needed AI resources
    not_a_real_test = '''
    def test_run_me_to_create_needed_resources_for_other_tests(self, ai_client: AIClient):
        new_local_resource = AIResource(
            name="e2e_test_resource_1",
            description="e2e testing resource. Do NOT DELETE",
            resource_group=ai_client.resource_group_name,
        )
        created_poller = ai_client.ai_resources.begin_create(ai_resource=new_local_resource)
        new_local_resource = AIResource(
            name="e2e_test_resource_2",
            description="e2e testing resource. Do NOT DELETE",
            resource_group=ai_client.resource_group_name,
        )
        created_poller = ai_client.ai_resources.begin_create(ai_resource=new_local_resource)
    '''


    def test_resource_get_and_list(self, ai_client_with_ai_access: AIClient):
        expected_resources = ["e2e_test_resource_1", "e2e_test_resource_2"]
        resources = ai_client_with_ai_access.ai_resources.list()
        assert len(resources) >= len(expected_resources)
        expected_count = 0
        for listed_resource in resources:
            name = listed_resource.name

            if name in expected_resources:
                expected_count += 1
                gotten_resource = ai_client_with_ai_access.ai_resources.get(name=name)
                assert gotten_resource.name == name

        assert expected_count == len(expected_resources)

    # DEV NOTE: due to how long it takes for 3 LROPollers to resolve, this test can easily take a couple minutes to run in live mode
    def test_create_update_and_delete(self, ai_client_with_ai_access: AIClient):
        new_local_resource = AIResource(
            name="e2e_test_resource_" + "".join(random.choice(string.digits) for _ in range(10)),
            description="Transient test object. Delete if seen.",
            resource_group=ai_client_with_ai_access.resource_group_name,
        )
        created_poller = ai_client_with_ai_access.ai_resources.begin_create(ai_resource=new_local_resource)
        created_resource = created_poller.result()
        assert new_local_resource.name == created_resource.name
        assert new_local_resource.description == created_resource.description

        delete_poller = ai_client_with_ai_access.ai_resources.begin_delete(
            name=new_local_resource.name, delete_dependent_resources=True
        )
        delete_poller.wait()
        with pytest.raises(ResourceNotFoundError):
            ai_client_with_ai_access.ai_resources.get(name=new_local_resource.name)
