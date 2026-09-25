# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import functools

from devtools_testutils import (
    AzureRecordedTestCase,
    PowerShellPreparer,
    recorded_by_proxy,
)
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextPiiResult,
    EntitySynonym,
    EntitySynonyms,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiActionContent,
    TextPiiEntitiesRecognitionInput,
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
    def test_recognize_pii_entity_synonyms(self, text_analysis_endpoint):
        client = self.create_client(text_analysis_endpoint)
        entity_synonyms = EntitySynonyms(
            entity_type="USBankAccountNumber",
            synonyms=[
                EntitySynonym(synonym="BANK", language="en"),
                EntitySynonym(synonym="BAN", language="en"),
            ],
        )
        body = TextPiiEntitiesRecognitionInput(
            text_input=MultiLanguageTextInput(
                multi_language_inputs=[
                    MultiLanguageInput(
                        id="A", text="My BANK is 123456789.", language="en"
                    )
                ]
            ),
            action_content=PiiActionContent(entity_synonyms=[entity_synonyms]),
        )

        result = client.analyze_text(body=body)

        assert isinstance(result, AnalyzeTextPiiResult)
        assert result.results is not None
        assert result.results.documents is not None
        assert any(
            entity.category == "USBankAccountNumber"
            for document in result.results.documents
            for entity in document.entities
        )
