# pylint: disable=line-too-long,useless-suppression
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
    TextPiiEntitiesRecognitionInput,
    AnalyzeTextPiiResult,
    PiiResultWithDetectedLanguage,
    PiiEntity,
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
    async def test_analyze_text_recognize_pii_async(self, text_analysis_endpoint, text_analysis_key):
        async with self.create_client(text_analysis_endpoint, text_analysis_key) as client:
            text_a = (
                "Parker Doe has repaid all of their loans as of 2020-04-25. Their SSN is 859-98-0987. To contact them, "
                "use their phone number 800-102-1100. They are originally from Brazil and have document ID number "
                "998.214.865-68."
            )

            body = TextPiiEntitiesRecognitionInput(
                text_input=MultiLanguageTextInput(
                    multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
                )
            )

            # Async (non-LRO) call
            result = await client.analyze_text(body=body)

            assert result is not None
            assert isinstance(result, AnalyzeTextPiiResult)

            assert result.results is not None
            assert result.results.documents is not None

            for doc in result.results.documents:
                assert isinstance(doc, PiiResultWithDetectedLanguage)
                assert doc.id is not None
                assert doc.entities is not None

                for entity in doc.entities:
                    assert isinstance(entity, PiiEntity)
                    assert entity.text is not None
                    assert entity.category is not None
                    assert entity.offset is not None
                    assert entity.length is not None
                    assert entity.confidence_score is not None
