# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_extract_key_phrases_async.py

DESCRIPTION:
    This sample demonstrates how to run **key phrase extraction** over text (async).

USAGE:
    python sample_extract_key_phrases_async.py

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

# [START extract_key_phrases_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextKeyPhraseExtractionInput,
    KeyPhraseActionContent,
    AnalyzeTextKeyPhraseResult,
)


async def sample_extract_key_phrases_async():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    async with TextAnalysisClient(endpoint, credential=credential) as client:
        # Build input
        text_a = (
            "We love this trail and make the trip every year. The views are breathtaking and well worth the hike! "
            "Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was "
            "amazing. Everyone in my family liked the trail although it was too challenging for the less "
            "athletic among us. Not necessarily recommended for small children. A hotel close to the trail "
            "offers services for childcare in case you want that."
        )

        body = TextKeyPhraseExtractionInput(
            text_input=MultiLanguageTextInput(
                multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
            ),
            action_content=KeyPhraseActionContent(model_version="latest"),
        )

        result = await client.analyze_text(body=body)

        # Validate and print results
        if not isinstance(result, AnalyzeTextKeyPhraseResult):
            print("Unexpected result type.")
            return

        if result.results is None:
            print("No results returned.")
            return

        if result.results.documents is None or len(result.results.documents) == 0:
            print("No documents in the response.")
            return

        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            if doc.key_phrases:
                print("Key Phrases:")
                for phrase in doc.key_phrases:
                    print(f"  - {phrase}")
            else:
                print("No key phrases found for this document.")
# [END extract_key_phrases_async]


async def main():
    await sample_extract_key_phrases_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
