# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities_with_excluded_categories_async.py

DESCRIPTION:
    This sample demonstrates how to exclude PII categories from entity recognition asynchronously.

USAGE:
    python sample_recognize_pii_entities_with_excluded_categories_async.py

REQUIRED ENV VARS:
    AZURE_TEXT_ENDPOINT
"""

# [START recognize_pii_entities_with_excluded_categories_async]
import asyncio
import os

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextPiiResult,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiActionContent,
    TextPiiEntitiesRecognitionInput,
)


async def sample_recognize_pii_entities_with_excluded_categories_async():
    credential = DefaultAzureCredential()
    async with credential, TextAnalysisClient(
        endpoint=os.environ["AZURE_TEXT_ENDPOINT"],
        credential=credential,
    ) as client:
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
        if isinstance(result, AnalyzeTextPiiResult) and result.results:
            for document in result.results.documents:
                print(f"Redacted text: {document.redacted_text}")
                for entity in document.entities:
                    print(f"{entity.text}: {entity.category} ({entity.confidence_score})")


# [END recognize_pii_entities_with_excluded_categories_async]


if __name__ == "__main__":
    asyncio.run(sample_recognize_pii_entities_with_excluded_categories_async())
