from azure.identity import DefaultAzureCredential
from azure.ai.generative._ai_client import AIClient

class TestFromConfig:
    def test_passes(self):
        credential = DefaultAzureCredential()
        ai_client = AIClient.from_config(credential=credential, path="samples/sample_config/config.json")
        assert(ai_client.subscription_id == "my_subscription_id")
        assert(ai_client.resource_group_name == "my_resource_group")
        assert(ai_client.project_name == "my_project_name")
