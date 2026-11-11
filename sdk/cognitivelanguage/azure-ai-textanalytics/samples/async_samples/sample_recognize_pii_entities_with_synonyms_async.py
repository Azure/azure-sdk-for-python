# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities_with_synonyms_async.py

DESCRIPTION:
    This sample demonstrates how to provide custom context synonyms for PII entity recognition asynchronously.

USAGE:
    python sample_recognize_pii_entities_with_synonyms_async.py

REQUIRED ENV VARS:
    AZURE_TEXT_ENDPOINT
"""

# [START recognize_pii_entities_with_synonyms_async]
import asyncio
import os

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextPiiResult,
    EntitySynonym,
    EntitySynonyms,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiActionContent,
    TextPiiEntitiesRecognitionInput,
)


async def sample_recognize_pii_entities_with_synonyms_async():
    credential = DefaultAzureCredential()
    async with credential, TextAnalysisClient(
        endpoint=os.environ["AZURE_TEXT_ENDPOINT"],
        credential=credential,
    ) as client:
        entity_synonyms = EntitySynonyms(
            entity_type="USBankAccountNumber",
            synonyms=[
                EntitySynonym(synonym="BANK", language="en"),
                EntitySynonym(synonym="BAN", language="en"),
            ],
        )
        body = TextPiiEntitiesRecognitionInput(
            text_input=MultiLanguageTextInput(
                multi_language_inputs=[MultiLanguageInput(id="A", text="My BANK is 123456789.", language="en")]
            ),
            action_content=PiiActionContent(entity_synonyms=[entity_synonyms]),
        )

        result = await client.analyze_text(body=body)
        if isinstance(result, AnalyzeTextPiiResult) and result.results:
            for document in result.results.documents:
                for entity in document.entities:
                    print(f"{entity.text}: {entity.category} ({entity.confidence_score})")


# [END recognize_pii_entities_with_synonyms_async]


if __name__ == "__main__":
    asyncio.run(sample_recognize_pii_entities_with_synonyms_async())
