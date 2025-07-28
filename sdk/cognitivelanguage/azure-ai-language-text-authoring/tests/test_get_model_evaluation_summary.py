# pylint: disable=line-too-long,useless-suppression
import functools
from urllib import response
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.text.authoring import TextAuthoringClient
from azure.ai.language.text.authoring.models import (
    TextAuthoringProjectKind,
    CustomSingleLabelClassificationEvalSummary
)
from azure.core.credentials import AzureKeyCredential

TextPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="fake_resource.servicebus.windows.net/",
    authoring_key="fake_key",
)

class TestText(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = TextAuthoringClient(endpoint, credential)
        return client

    ...

class TestTextCase(TestText):
    @TextPreparer()
    @recorded_by_proxy
    def test_get_model_evaluation_summary(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "single-class-project"
        trained_model_label = "model1"

        trained_model_client = client.get_trained_model_client(project_name, trained_model_label)

        evaluation_summary = trained_model_client.get_model_evaluation_summary()

         # Assert: base checks
        assert evaluation_summary is not None
        assert evaluation_summary.project_kind is not None
        assert evaluation_summary.evaluation_options is not None

        print(f"Project Kind: {evaluation_summary.project_kind}")
        print(f"Evaluation Options: {evaluation_summary.evaluation_options}")

        # Branch by project kind
        if evaluation_summary.project_kind == TextAuthoringProjectKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION:
            assert isinstance(evaluation_summary, CustomSingleLabelClassificationEvalSummary)
            summary = evaluation_summary.custom_single_label_classification_evaluation

            # Check micro/macro metrics
            assert summary.micro_f1 is not None
            assert summary.micro_precision is not None
            assert summary.micro_recall is not None
            assert summary.macro_f1 is not None
            assert summary.macro_precision is not None
            assert summary.macro_recall is not None

            print(f"Micro F1: {summary.micro_f1}")
            print(f"Macro Precision: {summary.macro_precision}")

            # Confusion Matrix
            if summary.confusion_matrix:
                for row_key, row in summary.confusion_matrix.items():
                    for col_key, cell in row.items():
                        assert "normalizedValue" in cell
                        assert "rawValue" in cell
                        print(
                            f"[ConfusionMatrix] Row={row_key}, Col={col_key}, "
                            f"Normalized={cell['normalizedValue']}, Raw={cell['rawValue']}"
                        )

            # Class-Specific Metrics
            if summary.classes:
                for class_name, metrics in summary.classes.items():
                    assert metrics.f1 is not None
                    assert metrics.precision is not None
                    assert metrics.recall is not None
                    print(f"[Class={class_name}] F1={metrics.f1}, Precision={metrics.precision}, Recall={metrics.recall}")

        else:
            pytest.skip(f"Project kind {evaluation_summary.project_kind} is not supported in this test.")