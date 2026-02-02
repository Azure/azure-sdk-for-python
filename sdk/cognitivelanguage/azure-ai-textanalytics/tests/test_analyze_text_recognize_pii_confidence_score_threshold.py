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
    ConfidenceScoreThreshold,
    ConfidenceScoreThresholdOverride,
    PiiActionContent,
)

TextAnalysisPreparer = functools.partial(
    EnvironmentVariableLoader,
    "text_analysis",
    text_analysis_endpoint="https://Sanitized.azure-api.net/",
    text_analysis_key="fake_key",
)


class TestTextAnalysis(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAnalysisClient:
        return TextAnalysisClient(endpoint, AzureKeyCredential(key))


class TestTextAnalysisCase_NewPIIThresholds(TestTextAnalysis):
    @TextAnalysisPreparer()
    @recorded_by_proxy
    def test_analyze_text_recognize_pii_confidence_score_threshold(self, text_analysis_endpoint, text_analysis_key):
        client = self.create_client(text_analysis_endpoint, text_analysis_key)

        # Input documents
        docs = [
            MultiLanguageInput(
                id="1",
                text="My name is John Doe. My ssn is 222-45-6789. My email is john@example.com. John Doe is my name.",
                language="en",
            )
        ]
        text_input = MultiLanguageTextInput(multi_language_inputs=docs)

        # Confidence score overrides
        ssn_override = ConfidenceScoreThresholdOverride(value=0.9, entity="USSocialSecurityNumber")
        email_override = ConfidenceScoreThresholdOverride(value=0.9, entity="Email")
        confidence_threshold = ConfidenceScoreThreshold(default=0.3, overrides=[ssn_override, email_override])
        # Parameters
        parameters = PiiActionContent(
            pii_categories=["All"], confidence_score_threshold=confidence_threshold
        )

        body = TextPiiEntitiesRecognitionInput(text_input=text_input, action_content=parameters)

        # Sync call
        result = client.analyze_text(body=body)

        # Basic result shape checks
        assert result is not None
        assert isinstance(result, AnalyzeTextPiiResult)
        assert result.results is not None
        assert result.results.documents is not None

        doc = result.results.documents[0]
        redacted = doc.redacted_text

        # Person should be masked out in text; SSN & Email should remain (filtered out as entities)
        assert "John Doe" not in redacted
        assert doc.entities is not None
        assert len(doc.entities) > 0

        # Person is present
        assert any(e.category == "Person" for e in doc.entities), "Expected at least one Person entity"

        # Verify SSN / Email are NOT returned as entities
        bad_categories = {"USSocialSecurityNumber", "Email"}
        bad_types = {"USSocialSecurityNumber", "Email"}

        for e in doc.entities:
            assert e.category not in bad_categories
            assert e.type not in bad_types
