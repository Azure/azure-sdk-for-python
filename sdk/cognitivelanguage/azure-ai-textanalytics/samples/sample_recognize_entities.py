# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_entities.py

DESCRIPTION:
    This sample demonstrates how to run **entity recognition** over text.

USAGE:
    python sample_recognize_entities.py

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

# [START recognize_entities]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextEntityRecognitionInput,
    EntitiesActionContent,
    AnalyzeTextEntitiesResult,
)


def sample_recognize_entities():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # input
    text_a = (
        "We love this trail and make the trip every year. The views are breathtaking and well worth the hike! "
        "Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was "
        "amazing. Everyone in my family liked the trail although it was too challenging for the less "
        "athletic among us. Not necessarily recommended for small children. A hotel close to the trail "
        "offers services for childcare in case you want that."
    )

    body = TextEntityRecognitionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        ),
        action_content=EntitiesActionContent(model_version="latest"),
    )

    result = client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextEntitiesResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            if doc.entities:
                print("Entities:")
                for entity in doc.entities:
                    print(f"  Text: {entity.text}")
                    print(f"  Category: {entity.category}")
                    if entity.subcategory:
                        print(f"  Subcategory: {entity.subcategory}")
                    print(f"  Offset: {entity.offset}")
                    print(f"  Length: {entity.length}")
                    print(f"  Confidence score: {entity.confidence_score}\n")
            else:
                print("No entities found for this document.")
    else:
        print("No documents in the response or unexpected result type.")

# [END recognize_entities]


def main():
    sample_recognize_entities()


if __name__ == "__main__":
    main()
