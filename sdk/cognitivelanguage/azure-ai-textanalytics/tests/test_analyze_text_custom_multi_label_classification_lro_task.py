import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    CustomMultiLabelClassificationActionContent,
    CustomMultiLabelClassificationOperationAction,
    TextActions,
    CustomMultiLabelClassificationOperationResult,
    ClassificationActionResult,
    ClassificationResult,
)

TextAnalysisPreparer = functools.partial(
    EnvironmentVariableLoader,
    "text_analysis",
    text_analysis_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    text_analysis_key="fake_key",
)


class TestTextAnalysis(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAnalysisClient:
        return TextAnalysisClient(endpoint, AzureKeyCredential(key))


class TestTextAnalysisCase(TestTextAnalysis):
    @TextAnalysisPreparer()
    @recorded_by_proxy
    def test_analyze_text_custom_multi_label_classification_lro_task(self, text_analysis_endpoint, text_analysis_key):
        client = self.create_client(text_analysis_endpoint, text_analysis_key)

        project_name = "multi-class-project"
        deployment_name = "multiclassdeployment"

        text_a = (
            "I need a reservation for an indoor restaurant in China. Please don't stop the music. "
            "Play music and add it to my playlist."
        )

        text_input = MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        )

        # Start LRO (sync) – actions defined inline
        poller = client.begin_analyze_text_job(
            text_input=text_input,
            actions=[
                CustomMultiLabelClassificationOperationAction(
                    name="CMCOperationActionSample",
                    action_content=CustomMultiLabelClassificationActionContent(
                        project_name=project_name,
                        deployment_name=deployment_name,
                    ),
                )
            ],
        )

        assert poller is not None
        paged_actions = poller.result()
        details = poller.details
        assert "operation_id" in details
        assert details.get("status") is not None
        assert paged_actions is not None

        found_cmc = False

        for actions_page in paged_actions:
            # Page container holding job results
            assert isinstance(actions_page, TextActions)
            assert actions_page.items_property is not None  # wire: "items"

            for op_result in actions_page.items_property:
                if isinstance(op_result, CustomMultiLabelClassificationOperationResult):
                    found_cmc = True
                    result = op_result.results
                    assert result is not None
                    assert result.documents is not None

                    for doc in result.documents:
                        assert isinstance(doc, ClassificationActionResult)
                        assert doc.id is not None

                        assert doc.class_property is not None
                        for cls_item in doc.class_property:
                            assert isinstance(cls_item, ClassificationResult)
                            assert cls_item.category is not None
                            assert cls_item.confidence_score is not None

        assert found_cmc, "Expected a CustomMultiLabelClassificationOperationResult in TextActions.items_property"
