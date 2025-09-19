# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_detect_language.py

DESCRIPTION:
    This sample demonstrates how to run **language detection** over text.

USAGE:
    python sample_detect_language.py

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

# [START detect_language]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    TextLanguageDetectionInput,
    LanguageDetectionTextInput,
    LanguageInput,
    AnalyzeTextLanguageDetectionResult,
)


def sample_detect_language():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # Build input
    text_a = (
        "Sentences in different languages."
    )

    body = TextLanguageDetectionInput(
        text_input=LanguageDetectionTextInput(
            language_inputs=[LanguageInput(id="A", text=text_a)]
        )
    )

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

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

# [END detect_language]


def main():
    sample_detect_language()


if __name__ == "__main__":
    main()
