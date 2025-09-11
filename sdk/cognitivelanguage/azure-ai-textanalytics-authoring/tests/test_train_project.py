# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.models import (
    TrainingJobDetails,
    EvaluationDetails,
    EvaluationKind,
)

AuthoringPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestTextAuthoring(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAuthoringClient:
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))


class TestTextAuthoringTrain(TestTextAuthoring):
    @AuthoringPreparer()
    @recorded_by_proxy
    def test_train_project(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "single-class-project"
        project_client = client.get_project_client(project_name)

        # Arrange – object model (snake_case), as in conversation authoring reference
        training_job_details = TrainingJobDetails(
            model_label="model0902",
            training_config_version="2022-05-01",
            evaluation_options=EvaluationDetails(
                kind=EvaluationKind.PERCENTAGE,
                testing_split_percentage=20,
                training_split_percentage=80,
            ),
        )

        poller = project_client.project.begin_train(body=training_job_details)

        try:
            poller.result()
        except HttpResponseError as e:
            msg = getattr(getattr(e, "error", None), "message", str(e))
            print(f"Operation failed: {msg}")
            raise

        print(f"Import completed. done={poller.done()} status={poller.status()}")
