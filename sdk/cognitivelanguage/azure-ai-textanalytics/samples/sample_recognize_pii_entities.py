# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities.py

DESCRIPTION:
    This sample demonstrates how to run **PII entity recognition** over text.

USAGE:
    python sample_recognize_pii_entities.py

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

# [START recognize_pii_entities]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextPiiEntitiesRecognitionInput,
    AnalyzeTextPiiResult,
)


def sample_recognize_pii_entities():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # input
    text_a = (
        "Parker Doe has repaid all of their loans as of 2020-04-25. Their SSN is 859-98-0987. "
        "To contact them, use their phone number 800-102-1100. They are originally from Brazil and "
        "have document ID number 998.214.865-68."
    )

    body = TextPiiEntitiesRecognitionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        )
    )

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextPiiResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            if doc.entities:
                print("PII Entities:")
                for entity in doc.entities:
                    print(f"  Text: {entity.text}")
                    print(f"  Category: {entity.category}")
                    # subcategory may be optional
                    if entity.subcategory:
                        print(f"  Subcategory: {entity.subcategory}")
                    print(f"  Offset: {entity.offset}")
                    print(f"  Length: {entity.length}")
                    print(f"  Confidence score: {entity.confidence_score}\n")
            else:
                print("No PII entities found for this document.")
    else:
        print("No documents in the response or unexpected result type.")

# [END recognize_pii_entities]


def main():
    sample_recognize_pii_entities()


if __name__ == "__main__":
    main()
