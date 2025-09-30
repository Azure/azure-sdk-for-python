# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_detect_language_async.py

DESCRIPTION:
    This sample demonstrates how to run **language detection** over text (async).

USAGE:
    python sample_detect_language_async.py

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

# [START detect_language_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    TextLanguageDetectionInput,
    LanguageDetectionTextInput,
    LanguageInput,
    AnalyzeTextLanguageDetectionResult,
)


async def sample_detect_language_async():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    async with TextAnalysisClient(endpoint, credential=credential) as client:
        # Build input
        text_a = (
            "Sentences in different languages."
        )

        body = TextLanguageDetectionInput(
            text_input=LanguageDetectionTextInput(
                language_inputs=[LanguageInput(id="A", text=text_a)]
            )
        )

        # Async (non-LRO) call
        result = await client.analyze_text(body=body)

        # Validate and print results
        if not isinstance(result, AnalyzeTextLanguageDetectionResult):
            print("Unexpected result type.")
            return

        if not result.results or not result.results.documents:
            print("No documents in the response.")
            return

        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            if doc.detected_language:
                dl = doc.detected_language
                print(f"Detected language: {dl.name} ({dl.iso6391_name})")
                print(f"Confidence score: {dl.confidence_score}")
            else:
                print("No detected language returned for this document.")
# [END detect_language_async]


async def main():
    await sample_detect_language_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
