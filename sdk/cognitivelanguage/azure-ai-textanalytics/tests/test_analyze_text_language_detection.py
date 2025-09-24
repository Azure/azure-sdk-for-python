import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    TextLanguageDetectionInput,
    LanguageDetectionTextInput,
    LanguageInput,
    AnalyzeTextLanguageDetectionResult,
    LanguageDetectionDocumentResult,
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
    def test_analyze_text_language_detection(self, text_analysis_endpoint, text_analysis_key):
        client = self.create_client(text_analysis_endpoint, text_analysis_key)

        text_a = "Sentences in different languages."

        body = TextLanguageDetectionInput(
            text_input=LanguageDetectionTextInput(language_inputs=[LanguageInput(id="A", text=text_a)])
        )

        result = client.analyze_text(body=body)

        assert result is not None
        assert isinstance(result, AnalyzeTextLanguageDetectionResult)

        assert result.results is not None
        assert result.results.documents is not None

        for doc in result.results.documents:
            assert isinstance(doc, LanguageDetectionDocumentResult)
            assert doc.id is not None
            assert doc.detected_language is not None
            assert doc.detected_language.name is not None
            assert doc.detected_language.iso6391_name is not None
            assert doc.detected_language.confidence_score is not None
