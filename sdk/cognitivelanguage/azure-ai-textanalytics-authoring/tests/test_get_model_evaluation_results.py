# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CustomSingleLabelClassificationDocumentEvalResult,
)

AuthoringPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestTextAuthoring(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))


class TestTextAuthoringGetModelEvaluationResultsSync(TestTextAuthoring):
    @AuthoringPreparer()
    @recorded_by_proxy
    def test_get_model_evaluation_results(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "single-class-project"
        trained_model_label = "model3"

        # Trained-model–scoped call
        project_client = client.get_project_client(project_name)
        results = project_client.trained_model.list_model_evaluation_results(
            trained_model_label,
            string_index_type="UTF16CodeUnit",
        )

        # Assert the pager exists
        assert results is not None, "The evaluation results should not be null."

        for result in results:
            # Base validations
            assert result is not None, "The result should not be null."
            assert result.location is not None, "The result location should not be null."
            assert result.language is not None, "The result language should not be null."

            # Validate classification result
            if isinstance(result, CustomSingleLabelClassificationDocumentEvalResult):
                classification = result.custom_single_label_classification_result
                assert classification is not None, "The classification result should not be null."
                assert (
                    classification.expected_class and classification.expected_class.strip()
                ), "The expected class should not be null or empty."
                assert (
                    classification.predicted_class and classification.predicted_class.strip()
                ), "The predicted class should not be null or empty."

                # Optional: print a couple of fields for recording visibility
                print(f"Document Location: {result.location}")
                print("  Classification:")
                print(f"    Expected: {classification.expected_class}")
                print(f"    Predicted: {classification.predicted_class}")
            else:
                raise AssertionError(f"Unsupported result type: {type(result).__name__}")
