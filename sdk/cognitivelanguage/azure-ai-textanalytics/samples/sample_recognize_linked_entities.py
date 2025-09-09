# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_linked_entities.py

DESCRIPTION:
    This sample demonstrates how to run **entity linking** over text.

USAGE:
    python sample_recognize_linked_entities.py

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

# [START recognize_linked_entities]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextEntityLinkingInput,
    EntityLinkingActionContent,
    AnalyzeTextEntityLinkingResult,
)


def sample_recognize_linked_entities():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

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

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

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

# [END recognize_linked_entities]


def main():
    sample_recognize_linked_entities()


if __name__ == "__main__":
    main()
