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
    PiiActionContent,
    EntityMaskPolicyType,
    CharacterMaskPolicyType,
    SyntheticReplacementPolicyType,
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
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_analyze_text_recognize_pii_redaction_policies_async(self, text_analysis_endpoint, text_analysis_key):
        async with self.create_client(text_analysis_endpoint, text_analysis_key) as client:

            # Documents
            documents = [
                MultiLanguageInput(
                    id="1",
                    text="My name is John Doe. My ssn is 123-45-6789. My email is john@example.com..",
                    language="en",
                ),
                MultiLanguageInput(
                    id="2",
                    text="My name is John Doe. My ssn is 123-45-6789. My email is john@example.com..",
                    language="en",
                ),
            ]

            text_input = MultiLanguageTextInput(multi_language_inputs=documents)

            # Redaction Policies
            default_policy = EntityMaskPolicyType(policy_name="defaultPolicy", is_default_policy=True)

            ssn_policy = CharacterMaskPolicyType(
                policy_name="customMaskForSSN",
                unmask_length=4,
                unmask_from_end=False,
                entity_types=["USSocialSecurityNumber"],
            )

            synthetic_policy = SyntheticReplacementPolicyType(
                policy_name="syntheticMaskForPerson", entity_types=["Person", "Email"]
            )

            parameters = PiiActionContent(
                pii_categories=["All"], redaction_policies=[default_policy, ssn_policy, synthetic_policy]
            )

            body = TextPiiEntitiesRecognitionInput(text_input=text_input, action_content=parameters)

            # Async (non-LRO) call
            result = await client.analyze_text(body=body)

            # Basic validation
            assert result is not None
            assert isinstance(result, AnalyzeTextPiiResult)
            assert result.results is not None
            assert result.results.documents is not None
            assert len(result.results.documents) == 2

            for doc in result.results.documents:
                assert isinstance(doc, PiiResultWithDetectedLanguage)
                assert doc.id in ("1", "2")

                # Entities exist
                assert doc.entities is not None and len(doc.entities) > 0

                # Check redaction
                assert doc.redacted_text is not None
                redacted_text = doc.redacted_text

                # Ensure original PII not present
                assert "123-45-6789" not in redacted_text
                assert "john@example.com" not in redacted_text
                assert "John Doe" not in redacted_text

                # Check at least one of each category detected
                categories = {e.category.lower() for e in doc.entities}
                assert any("ssn" in c or "socialsecurity" in c for c in categories)
                assert any("email" in c for c in categories)
                assert any("person" in c for c in categories)

                # Check each entity has required fields
                for entity in doc.entities:
                    assert isinstance(entity, PiiEntity)
                    assert entity.text is not None
                    assert entity.category is not None
                    assert entity.offset is not None
                    assert entity.length is not None
                    assert entity.confidence_score is not None
