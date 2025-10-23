import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextEntityRecognitionInput,
    EntitiesActionContent,
    AnalyzeTextEntitiesResult,
    EntityActionResult,
    NamedEntityWithMetadata,
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
    def test_analyze_text_recognize_entities(self, text_analysis_endpoint, text_analysis_key):
        client = self.create_client(text_analysis_endpoint, text_analysis_key)

        text_a = (
            "We love this trail and make the trip every year. The views are breathtaking and well worth the hike! "
            "Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was "
            "amazing. Everyone in my family liked the trail although it was too challenging for the less "
            "athletic among us. Not necessarily recommended for small children. A hotel close to the trail "
            "offers services for childcare in case you want that."
        )

        body = TextEntityRecognitionInput(
            text_input=MultiLanguageTextInput(
                multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
            ),
            action_content=EntitiesActionContent(model_version="latest"),
        )

        # Sync (non-LRO) call
        result = client.analyze_text(body=body)

        assert result is not None
        assert isinstance(result, AnalyzeTextEntitiesResult)

        assert result.results is not None
        assert result.results.documents is not None

        for doc in result.results.documents:
            assert isinstance(doc, EntityActionResult)
            assert doc.id is not None
            assert doc.entities is not None

            for entity in doc.entities:
                assert isinstance(entity, NamedEntityWithMetadata)
                assert entity.text is not None
                assert entity.category is not None
                assert entity.offset is not None
                assert entity.length is not None
                assert entity.confidence_score is not None
