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
    ConfidenceScoreThreshold,
    ConfidenceScoreThresholdOverride,
    PiiActionContent,
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


class TestTextAnalysisCase_NewPIIThresholds(TestTextAnalysis):
    @TextAnalysisPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_analyze_text_recognize_pii_confidence_score_threshold_async(self, text_analysis_endpoint, text_analysis_key):
        async with self.create_client(text_analysis_endpoint, text_analysis_key) as client:

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
            ssn_override_default = ConfidenceScoreThresholdOverride(value=0.8, entity="USSocialSecurityNumber")
            ssn_override_fr = ConfidenceScoreThresholdOverride(value=0.9, entity="USSocialSecurityNumber", language="fr")
            confidence_threshold = ConfidenceScoreThreshold(default= 0.9, overrides=[ssn_override_default, ssn_override_fr])

            # Parameters
            parameters = PiiActionContent(
                pii_categories=["All"], disable_entity_validation=True, confidence_score_threshold=confidence_threshold
            )

            body = TextPiiEntitiesRecognitionInput(text_input=text_input, action_content=parameters)

            # Async (non-LRO) call
            result = await client.analyze_text(body=body)

            # Basic result shape checks
            assert result is not None
            assert isinstance(result, AnalyzeTextPiiResult)
            assert result.results is not None
            assert result.results.documents is not None
            assert len(result.results.documents) == 1

            doc = result.results.documents[0]
            assert isinstance(doc, PiiResultWithDetectedLanguage)
            assert doc.id == "1"
            assert doc.entities is not None
            assert len(doc.entities) > 0

            # Validate entity fields + confidence thresholds apply
            saw_ssn = False
            for entity in doc.entities:
                assert isinstance(entity, PiiEntity)
                assert entity.text is not None
                assert entity.category is not None
                assert entity.offset is not None
                assert entity.length is not None
                assert entity.confidence_score is not None

                # For English doc, SSN should meet the 0.8 threshold override
                if entity.category in ("USSocialSecurityNumber", "SocialSecurityNumber", "ssn", "usssn"):
                    saw_ssn = True
                    assert entity.confidence_score >= 0.8

            # Ensure we actually recognized an SSN in the sample
            assert saw_ssn
