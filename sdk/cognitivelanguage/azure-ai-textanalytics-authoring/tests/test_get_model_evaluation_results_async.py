# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
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
    pass


class TestTextAuthoringGetModelEvaluationResultsAsync(TestTextAuthoring):
    @AuthoringPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_get_model_evaluation_results_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
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

            async for result in results:
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
