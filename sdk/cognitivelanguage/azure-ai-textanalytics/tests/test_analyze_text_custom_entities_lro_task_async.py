import functools
import pytest

from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    AnalyzeTextOperationAction,
    CustomEntitiesActionContent,
    CustomEntitiesLROTask,
    TextActions,
    CustomEntityRecognitionOperationResult,  # subclass of AnalyzeTextLROResult
    CustomEntityActionResult,
    NamedEntity,
)

TextAnalysisPreparer = functools.partial(
    EnvironmentVariableLoader,
    "text_analysis",
    text_analysis_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    text_analysis_key="fake_key",
)


class TestTextAnalysisAsync(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAnalysisClient:
        return TextAnalysisClient(endpoint, AzureKeyCredential(key))


class TestTextAnalysisCaseAsync(TestTextAnalysisAsync):
    @TextAnalysisPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_analyze_text_custom_entities_lro_task_async(self, text_analysis_endpoint, text_analysis_key):
        async with self.create_client(text_analysis_endpoint, text_analysis_key) as client:
            project_name = "Example-ner-project"
            deployment_name = "TestDeployment"
            text_a = (
                "We love this trail and make the trip every year. The views are breathtaking and well worth the hike! "
                "Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was "
                "amazing. Everyone in my family liked the trail although it was too challenging for the less "
                "athletic among us."
            )

            text_input = MultiLanguageTextInput(
                multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
            )

            action_content = CustomEntitiesActionContent(
                project_name=project_name,
                deployment_name=deployment_name,
            )

            actions: list[AnalyzeTextOperationAction] = [
                CustomEntitiesLROTask(
                    name="CustomEntitiesOperationActionSample",
                    parameters=action_content,
                )
            ]

            # Start LRO (async) – poller returns AsyncItemPaged[TextActions]
            poller = await client.begin_analyze_text_job(
                text_input=text_input,
                actions=actions,
            )

            assert poller is not None

            paged_actions = await poller.result()
            details = poller.details
            assert "operation_id" in details
            assert details.get("status") is not None
            assert paged_actions is not None

            found_custom_entities = False

            async for actions_page in paged_actions:
                # page payload container
                assert isinstance(actions_page, TextActions)
                assert actions_page.items_property is not None  # wire: "items"

                for op_result in actions_page.items_property:
                    if isinstance(op_result, CustomEntityRecognitionOperationResult):
                        found_custom_entities = True
                        result = op_result.results
                        assert result is not None
                        assert result.documents is not None

                        for doc in result.documents:
                            assert isinstance(doc, CustomEntityActionResult)
                            assert doc.id is not None
                            assert doc.entities is not None

                            for entity in doc.entities:
                                assert isinstance(entity, NamedEntity)
                                assert entity.text is not None
                                assert entity.category is not None
                                assert entity.offset is not None
                                assert entity.length is not None
                                assert entity.confidence_score is not None

            assert (
                found_custom_entities
            ), "Expected a CustomEntityRecognitionOperationResult in TextActions.items_property"
