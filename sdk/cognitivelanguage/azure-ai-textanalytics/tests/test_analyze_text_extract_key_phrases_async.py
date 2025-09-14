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
    TextKeyPhraseExtractionInput,
    KeyPhraseActionContent,
    AnalyzeTextKeyPhraseResult,
    KeyPhrasesActionResult,
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
    async def test_analyze_text_extract_key_phrases_async(self, text_analysis_endpoint, text_analysis_key):
        async with self.create_client(text_analysis_endpoint, text_analysis_key) as client:
            text_a = (
                "We love this trail and make the trip every year. The views are breathtaking and well worth the hike! "
                "Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was "
                "amazing. Everyone in my family liked the trail although it was too challenging for the less "
                "athletic among us. Not necessarily recommended for small children. A hotel close to the trail "
                "offers services for childcare in case you want that."
            )

            body = TextKeyPhraseExtractionInput(
                text_input=MultiLanguageTextInput(
                    multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
                ),
                action_content=KeyPhraseActionContent(model_version="latest"),
            )

            # Async (non-LRO) call
            result = await client.analyze_text(body=body)

            assert result is not None
            assert isinstance(result, AnalyzeTextKeyPhraseResult)

            assert result.results is not None
            assert result.results.documents is not None

            for doc in result.results.documents:
                assert isinstance(doc, KeyPhrasesActionResult)
                assert doc.id is not None
                assert doc.key_phrases is not None
                for key_phrase in doc.key_phrases:
                    assert key_phrase is not None
