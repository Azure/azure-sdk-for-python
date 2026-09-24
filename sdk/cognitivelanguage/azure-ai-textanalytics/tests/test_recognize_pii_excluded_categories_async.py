# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import functools

import pytest
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextPiiResult,
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


class TestTextAnalysisAsync(AzureRecordedTestCase):
    def create_client(self, endpoint: str) -> TextAnalysisClient:
        credential = self.get_credential(TextAnalysisClient, is_async=True)
        return self.create_client_from_credential(
            TextAnalysisClient,
            credential=credential,
            endpoint=endpoint,
        )


class TestTextAnalysisCaseAsync(TestTextAnalysisAsync):
    @TextAnalysisPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_recognize_pii_excluded_categories_async(self, text_analysis_endpoint):
        async with self.create_client(text_analysis_endpoint) as client:
            body = TextPiiEntitiesRecognitionInput(
                text_input=MultiLanguageTextInput(
                    multi_language_inputs=[
                        MultiLanguageInput(
                            id="A",
                            text="Call me at 800-102-1100. My SSN is 123-45-6789.",
                            language="en",
                        )
                    ]
                ),
                action_content=PiiActionContent(exclude_pii_categories=["PhoneNumber"]),
            )

            result = await client.analyze_text(body=body)

            assert isinstance(result, AnalyzeTextPiiResult)
            assert result.results is not None
            assert result.results.documents is not None
            document = result.results.documents[0]
            assert all(entity.category != "PhoneNumber" for entity in document.entities)
            assert any(entity.category == "USSocialSecurityNumber" for entity in document.entities)
            assert "800-102-1100" in document.redacted_text
            assert "123-45-6789" not in document.redacted_text
