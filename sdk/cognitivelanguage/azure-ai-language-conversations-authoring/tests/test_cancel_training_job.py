# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import TrainingJobResult

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsCancelTrainingSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_cancel_training_job(self, authoring_endpoint, authoring_key):
        
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "Test-data-labels"
        job_id = "b532b488-a546-4d25-a91c-89e21f056f62_638913312000000000"
        project_client = client.get_project_client(project_name)

        captured = {}

        def capture_initial_response(pipeline_response):
            # This hook is called for every HTTP response on this call.
            # Since polling=False, it will be the single initial response.
            http_resp = pipeline_response.http_response
            captured["status_code"] = http_resp.status_code
            captured["headers"] = http_resp.headers

        # Fire the cancel request but DO NOT poll; capture the initial response via hook.
        poller = project_client.project.begin_cancel_training_job(
            job_id=job_id,
            polling=False,
            raw_response_hook=capture_initial_response,
        )

        # Assert initial HTTP status
        assert captured.get("status_code") == 202, f"Expected 202, got {captured.get('status_code')}"

        # Print polling endpoints from headers
        headers = captured.get("headers", {})
        print(f"Operation-Location: {headers.get('Operation-Location') or headers.get('operation-location')}")
        print(f"Location: {headers.get('Location') or headers.get('location')}")

        # Optional: you still have a poller (NoPolling). Don't call poller.result() in this test.
        assert poller is not None