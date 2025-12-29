import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient
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


class TestTextAnalysis(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAnalysisClient:
        return TextAnalysisClient(endpoint, AzureKeyCredential(key))


class TestTextAnalysisCase(TestTextAnalysis):
    @TextAnalysisPreparer()
    @recorded_by_proxy
    def test_analyze_text_extract_key_phrases(self, text_analysis_endpoint, text_analysis_key):
        client = self.create_client(text_analysis_endpoint, text_analysis_key)

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

        # Sync (non-LRO) call
        result = client.analyze_text(body=body)

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
