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


class TestConversationsDeleteTrainedModelSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_delete_trained_model(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "Test-data-labels"
        trained_model_label = "model1"

        project_client = client.get_project_client(project_name)

        captured = {}

        def capture_response(pipeline_response):
            captured["status_code"] = pipeline_response.http_response.status_code

        # Act
        project_client.trained_model.delete_trained_model(trained_model_label, raw_response_hook=capture_response)

        # Print & Assert
        status = captured.get("status_code")
        print(f"Delete Trained Model Response Status: {status}")
        assert status == 204, f"Expected 204, got {status}"
