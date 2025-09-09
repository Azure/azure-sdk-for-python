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
    TextSentimentAnalysisInput,
    AnalyzeTextSentimentResult,
    SentimentActionResult,
    SentenceSentiment,
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
    async def test_analyze_text_sentiment_async(self, text_analysis_endpoint, text_analysis_key):
        async with self.create_client(text_analysis_endpoint, text_analysis_key) as client:
            text_a = (
                "The food and service were unacceptable, but the concierge were nice. After talking to them about the "
                "quality of the food and the process to get room service they refunded the money we spent at the "
                "restaurant and gave us a voucher for nearby restaurants."
            )

            body = TextSentimentAnalysisInput(
                text_input=MultiLanguageTextInput(
                    multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
                )
            )

            # Async (non-LRO) call
            result = await client.analyze_text(body=body)

            assert result is not None
            assert isinstance(result, AnalyzeTextSentimentResult)

            assert result.results is not None
            assert result.results.documents is not None

            for doc in result.results.documents:
                assert isinstance(doc, SentimentActionResult)
                assert doc.id is not None
                assert doc.sentiment is not None
                assert doc.confidence_scores is not None
                assert doc.confidence_scores.positive is not None
                assert doc.confidence_scores.neutral is not None
                assert doc.confidence_scores.negative is not None
                assert doc.sentences is not None

                for sentence in doc.sentences:
                    assert isinstance(sentence, SentenceSentiment)
                    assert sentence.text is not None
                    assert sentence.sentiment is not None
                    assert sentence.confidence_scores is not None
                    assert sentence.confidence_scores.positive is not None
                    assert sentence.confidence_scores.neutral is not None
                    assert sentence.confidence_scores.negative is not None
                    assert sentence.offset is not None
                    assert sentence.length is not None
