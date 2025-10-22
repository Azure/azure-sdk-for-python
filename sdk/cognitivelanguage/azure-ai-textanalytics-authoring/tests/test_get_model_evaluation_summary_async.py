# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CustomSingleLabelClassificationEvalSummary,
    EvaluationDetails,
)

AuthoringPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestTextAuthoring(AzureRecordedTestCase):
    pass


class TestTextAuthoringGetModelEvaluationSummaryAsync(TestTextAuthoring):
    @AuthoringPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_get_model_evaluation_summary_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
            project_name = "single-class-project"
            trained_model_label = "model3"

            # Trained-model–scoped call
            project_client = client.get_project_client(project_name)
            eval_summary = await project_client.trained_model.get_model_evaluation_summary(trained_model_label)

            # Assert the call returned something
            assert eval_summary is not None

            # Ensure we got a single-label classification evaluation summary
            assert isinstance(eval_summary, CustomSingleLabelClassificationEvalSummary)

            # Evaluation options must exist
            evaluation_options: EvaluationDetails = eval_summary.evaluation_options
            assert evaluation_options is not None
            print("Evaluation Options:")
            print(f"    Kind: {evaluation_options.kind}")
            print(f"    Training Split Percentage: {evaluation_options.training_split_percentage}")
            print(f"    Testing Split Percentage: {evaluation_options.testing_split_percentage}")

            # Classification evaluation must exist
            sl_eval = eval_summary.custom_single_label_classification_evaluation
            assert sl_eval is not None

            # Print micro/macro metrics
            print(f"Micro F1: {sl_eval.micro_f1}")
            print(f"Micro Precision: {sl_eval.micro_precision}")
            print(f"Micro Recall: {sl_eval.micro_recall}")
            print(f"Macro F1: {sl_eval.macro_f1}")
            print(f"Macro Precision: {sl_eval.macro_precision}")
            print(f"Macro Recall: {sl_eval.macro_recall}")

            # Confusion matrix
            cmatrix = sl_eval.confusion_matrix
            if cmatrix:
                print("Confusion Matrix:")
                for row_key, row_val in cmatrix.items():
                    print(f"Row: {row_key}")
                    for col_key, cell in row_val.items():
                        print(
                            f"    Column: {col_key}, Normalized Value: {cell['normalizedValue']}, Raw Value: {cell['rawValue']}"
                        )

            # Class-specific metrics
            classes_map = sl_eval.classes
            assert classes_map is not None and len(classes_map) > 0, "Class-specific metrics should not be empty."
            print("Class-Specific Metrics:")
            for cls_name, metrics in classes_map.items():
                print(f"Class: {cls_name}")
                print(f"    F1: {metrics.f1}")
                print(f"    Precision: {metrics.precision}")
                print(f"    Recall: {metrics.recall}")
                print(f"    True Positives: {metrics.true_positive_count}")
                print(f"    True Negatives: {metrics.true_negative_count}")
                print(f"    False Positives: {metrics.false_positive_count}")
                print(f"    False Negatives: {metrics.false_negative_count}")
