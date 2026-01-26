# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_pii_with_confidence_score_async.py

DESCRIPTION:
    This sample demonstrates how to run **PII entity recognition** with confidence score
    thresholds (async), including entity-specific overrides.

USAGE:
    python sample_pii_with_confidence_score_async.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
"""

# [START recognize_pii_entities_with_confidence_score_async]
import os
import asyncio # pylint:disable=do-not-import-asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageInput,
    MultiLanguageTextInput,
    TextPiiEntitiesRecognitionInput,
    PiiActionContent,
    ConfidenceScoreThreshold,
    ConfidenceScoreThresholdOverride,
    AnalyzeTextPiiResult,
)


async def sample_pii_with_confidence_score_async():
    # Settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    async with TextAnalysisClient(endpoint, credential=credential) as client:
        # Input text
        text = "My name is John Doe. My SSN is 222-45-6789. My email is john@example.com. John Doe is my name."

        # Confidence score thresholds:
        # - Default threshold is 0.3
        # - SSN & Email require 0.9 minimum confidence to be returned
        threshold = ConfidenceScoreThreshold(
            default=0.3,
            overrides=[
                ConfidenceScoreThresholdOverride(value=0.9, entity="USSocialSecurityNumber"),
                ConfidenceScoreThresholdOverride(value=0.9, entity="Email"),
            ],
        )

        body = TextPiiEntitiesRecognitionInput(
            text_input=MultiLanguageTextInput(
                multi_language_inputs=[MultiLanguageInput(id="1", text=text, language="en")]
            ),
            action_content=PiiActionContent(
                pii_categories=["All"],
                disable_entity_validation=True,
                confidence_score_threshold=threshold,
            ),
        )

        # Async (non-LRO) call
        result = await client.analyze_text(body=body)

        # Print results
        if isinstance(result, AnalyzeTextPiiResult) and result.results and result.results.documents:
            for doc in result.results.documents:
                print(f"\nDocument ID: {doc.id}")
                print(f"Redacted Text:\n  {doc.redacted_text}\n")

                print("Detected Entities (after threshold filtering):")
                if doc.entities:
                    for entity in doc.entities:
                        print(f"  Text: {entity.text}")
                        print(f"  Category: {entity.category}")
                        if entity.subcategory:
                            print(f"  Subcategory: {entity.subcategory}")
                        print(f"  Masked As: {entity.mask}")
                        print(f"  Confidence score: {entity.confidence_score}\n")
                else:
                    print("  No entities met the confidence threshold.")
        else:
            print("No documents in the response or unexpected result type.")


# [END recognize_pii_entities_with_confidence_score_async]


async def main():
    await sample_pii_with_confidence_score_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
