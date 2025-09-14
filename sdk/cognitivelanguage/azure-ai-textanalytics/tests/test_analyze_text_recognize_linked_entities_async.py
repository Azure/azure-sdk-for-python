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
    TextEntityLinkingInput,
    EntityLinkingActionContent,
    AnalyzeTextEntityLinkingResult,
    EntityLinkingActionResult,
    LinkedEntity,
    EntityLinkingMatch,
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
    async def test_analyze_text_recognize_linked_entities_async(self, text_analysis_endpoint, text_analysis_key):
        async with self.create_client(text_analysis_endpoint, text_analysis_key) as client:
            text_a = (
                "Microsoft was founded by Bill Gates with some friends he met at Harvard. One of his friends, Steve "
                "Ballmer, eventually became CEO after Bill Gates as well. Steve Ballmer eventually stepped down as "
                "CEO of Microsoft, and was succeeded by Satya Nadella. Microsoft originally moved its headquarters "
                "to Bellevue, Washington in January 1979, but is now headquartered in Redmond"
            )

            body = TextEntityLinkingInput(
                text_input=MultiLanguageTextInput(
                    multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
                ),
                action_content=EntityLinkingActionContent(model_version="latest"),
            )

            # Async (non-LRO) call
            result = await client.analyze_text(body=body)

            assert result is not None
            assert isinstance(result, AnalyzeTextEntityLinkingResult)

            assert result.results is not None
            assert result.results.documents is not None

            for doc in result.results.documents:
                assert isinstance(doc, EntityLinkingActionResult)
                assert doc.id is not None
                assert doc.entities is not None

                for linked in doc.entities:
                    assert isinstance(linked, LinkedEntity)
                    assert linked.name is not None
                    assert linked.language is not None
                    assert linked.data_source is not None
                    assert linked.url is not None
                    assert linked.id is not None
                    assert linked.matches is not None

                    for match in linked.matches:
                        assert isinstance(match, EntityLinkingMatch)
                        assert match.confidence_score is not None
                        assert match.text is not None
                        assert match.offset is not None
                        assert match.length is not None
