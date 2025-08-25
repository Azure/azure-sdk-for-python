# pylint: disable=line-too-long,useless-suppression
import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsGetDeploymentSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_get_deployment(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "EmailApp"
        deployment_name = "staging"

        project_client = client.get_project_client(project_name)

        # Act
        deployment = project_client.deployment.get_deployment(deployment_name=deployment_name)

        # Basic assertion
        assert deployment is not None

        print(f"Deployment Name: {getattr(deployment, 'deployment_name', None)}")
        print(f"Model Id: {getattr(deployment, 'model_id', None)}")
        print(f"Last Trained On: {getattr(deployment, 'last_trained_on', None)}")
        print(f"Last Deployed On: {getattr(deployment, 'last_deployed_on', None)}")
        print(f"Deployment Expired On: {getattr(deployment, 'deployment_expired_on', None)}")
        print(f"Model Training Config Version: {getattr(deployment, 'model_training_config_version', None)}")

        assigned_resources = getattr(deployment, "assigned_resources", None)
        if assigned_resources:
            for ar in assigned_resources:
                print(f"Resource ID: {getattr(ar, 'resource_id', None)}")
                print(f"Region: {getattr(ar, 'region', None)}")
                aoai = getattr(ar, "assigned_aoai_resource", None)
                if aoai:
                    print(f"AOAI Kind: {getattr(aoai, 'kind', None)}")
                    print(f"AOAI Resource ID: {getattr(aoai, 'resource_id', None)}")
                    print(f"AOAI Deployment Name: {getattr(aoai, 'deployment_name', None)}")
