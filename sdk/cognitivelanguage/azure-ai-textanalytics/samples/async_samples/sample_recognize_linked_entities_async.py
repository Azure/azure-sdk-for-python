# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_linked_entities_async.py

DESCRIPTION:
    This sample demonstrates how to run **entity linking** over text (async, non-LRO).

USAGE:
    python sample_recognize_linked_entities_async.py

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

# [START recognize_linked_entities_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextEntityLinkingInput,
    EntityLinkingActionContent,
    AnalyzeTextEntityLinkingResult,
)


async def sample_recognize_linked_entities_async():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    async with TextAnalysisClient(endpoint, credential=credential) as client:
        # input
        text_a = (
            "Microsoft was founded by Bill Gates with some friends he met at Harvard. One of his friends, Steve "
            "Ballmer, eventually became CEO after Bill Gates as well. Steve Ballmer eventually stepped down as "
            "CEO of Microsoft, and was succeeded by Satya Nadella. Microsoft originally moved its headquarters "
            "to Bellevue, Washington in January 1979, but is now headquartered in Redmond"
        )

        body = TextEntityLinkingInput(
            text_input=MultiLanguageTextInput(
                multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
            ),
            action_content=EntityLinkingActionContent(model_version="latest"),
        )

        # Async (non-LRO) call
        result = await client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextEntityLinkingResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            if not doc.entities:
                print("No linked entities found for this document.")
                continue

            print("Linked Entities:")
            for linked in doc.entities:
                print(f"  Name: {linked.name}")
                print(f"  Language: {linked.language}")
                print(f"  Data source: {linked.data_source}")
                print(f"  URL: {linked.url}")
                print(f"  ID: {linked.id}")

                if linked.matches:
                    print("  Matches:")
                    for match in linked.matches:
                        print(f"    Text: {match.text}")
                        print(f"    Confidence score: {match.confidence_score}")
                        print(f"    Offset: {match.offset}")
                        print(f"    Length: {match.length}")
                print()
    else:
        print("No documents in the response or unexpected result type.")

# [END recognize_linked_entities_async]


async def main():
    await sample_recognize_linked_entities_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
