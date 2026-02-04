# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsCancelTrainingSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_cancel_training_job(self, authoring_endpoint, authoring_key):

        client = self.create_client(authoring_endpoint, authoring_key)

        project_client = client.get_project_client("single-class-project")
        job_id = "8bfbd8e2-018f-4dfd-9f8f-75bf76410168_638931456000000000"

        poller = project_client.project.begin_cancel_training_job(
            job_id=job_id,
        )

        result = poller.result()  # TrainingJobResult

        assert (
            result.training_status.status == "succeeded"
        ), f"Cancellation failed with status: {result.training_status.status}"
        print(f"Model Label: {result.model_label}")
        print(f"Training Config Version: {result.training_config_version}")
        if result.training_status is not None:
            print(f"Training Status: {result.training_status.status}")
            print(f"Training %: {result.training_status.percent_complete}")
        if result.evaluation_status is not None:
            print(f"Evaluation Status: {result.evaluation_status.status}")
            print(f"Evaluation %: {result.evaluation_status.percent_complete}")
        print(f"Estimated End: {result.estimated_end_on}")
