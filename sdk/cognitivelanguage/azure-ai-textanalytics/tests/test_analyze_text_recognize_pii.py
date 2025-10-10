import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient
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


class TestTextAnalysis(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAnalysisClient:
        return TextAnalysisClient(endpoint, AzureKeyCredential(key))


class TestTextAnalysisCase(TestTextAnalysis):
    @TextAnalysisPreparer()
    @recorded_by_proxy
    def test_analyze_text_recognize_pii(self, text_analysis_endpoint, text_analysis_key):
        client = self.create_client(text_analysis_endpoint, text_analysis_key)

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

        # Sync (non-LRO) call
        result = client.analyze_text(body=body)

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
