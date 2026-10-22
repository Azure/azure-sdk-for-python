# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_extract_key_phrases.py

DESCRIPTION:
    This sample demonstrates how to run **key phrase extraction** over text.

USAGE:
    python sample_extract_key_phrases.py

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

# [START extract_key_phrases]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextKeyPhraseExtractionInput,
    KeyPhraseActionContent,
    AnalyzeTextKeyPhraseResult,
)


def sample_extract_key_phrases():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

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

    result = client.analyze_text(body=body)

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


# [END extract_key_phrases]


def main():
    sample_extract_key_phrases()


if __name__ == "__main__":
    main()
