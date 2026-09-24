# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities_with_excluded_categories.py

DESCRIPTION:
    This sample demonstrates how to exclude PII categories from entity recognition.

USAGE:
    python sample_recognize_pii_entities_with_excluded_categories.py

REQUIRED ENV VARS:
    AZURE_TEXT_ENDPOINT
"""

# [START recognize_pii_entities_with_excluded_categories]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextPiiResult,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiActionContent,
    TextPiiEntitiesRecognitionInput,
)


def sample_recognize_pii_entities_with_excluded_categories():
    client = TextAnalysisClient(
        endpoint=os.environ["AZURE_TEXT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    body = TextPiiEntitiesRecognitionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[
                MultiLanguageInput(
                    id="A",
                    text="Call me at 800-102-1100. My SSN is 123-45-6789.",
                    language="en",
                )
            ]
        ),
        action_content=PiiActionContent(exclude_pii_categories=["PhoneNumber"]),
    )

    result = client.analyze_text(body=body)
    if isinstance(result, AnalyzeTextPiiResult) and result.results:
        for document in result.results.documents:
            print(f"Redacted text: {document.redacted_text}")
            for entity in document.entities:
                print(f"{entity.text}: {entity.category} ({entity.confidence_score})")


# [END recognize_pii_entities_with_excluded_categories]


if __name__ == "__main__":
    sample_recognize_pii_entities_with_excluded_categories()
