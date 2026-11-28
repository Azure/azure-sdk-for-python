# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import functools

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextPiiResult,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiActionContent,
    TextPiiEntitiesRecognitionInput,
    ValueExclusionPolicy,
)

TextAnalysisPreparer = functools.partial(
    PowerShellPreparer,
    "text_analysis",
    text_analysis_endpoint="https://Sanitized.cognitiveservices.azure.com/",
)


class TestTextAnalysis(AzureRecordedTestCase):
    def create_client(self, endpoint: str) -> TextAnalysisClient:
        credential = self.get_credential(TextAnalysisClient)
        return self.create_client_from_credential(
            TextAnalysisClient,
            credential=credential,
            endpoint=endpoint,
        )


class TestTextAnalysisCase(TestTextAnalysis):
    @TextAnalysisPreparer()
    @recorded_by_proxy
    def test_recognize_pii_value_exclusion_policy(self, text_analysis_endpoint):
        client = self.create_client(text_analysis_endpoint)
        body = TextPiiEntitiesRecognitionInput(
            text_input=MultiLanguageTextInput(
                multi_language_inputs=[
                    MultiLanguageInput(
                        id="A",
                        text="My name is John Doe and my SSN is 123-45-6789.",
                        language="en",
                    )
                ]
            ),
            action_content=PiiActionContent(
                value_exclusion_policy=ValueExclusionPolicy(
                    case_sensitive=False,
                    excluded_values=["John Doe"],
                )
            ),
        )

        result = client.analyze_text(body=body)

        assert isinstance(result, AnalyzeTextPiiResult)
        assert result.results is not None
        assert result.results.documents is not None
        document = result.results.documents[0]
        assert all(entity.text != "John Doe" for entity in document.entities)
        assert any(entity.category == "USSocialSecurityNumber" for entity in document.entities)
        assert "John Doe" in document.redacted_text
        assert "123-45-6789" not in document.redacted_text
