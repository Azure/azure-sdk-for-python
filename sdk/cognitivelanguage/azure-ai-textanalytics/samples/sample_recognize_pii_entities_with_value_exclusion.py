# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities_with_value_exclusion.py

DESCRIPTION:
    This sample demonstrates how to exclude specific values from PII entity recognition.

USAGE:
    python sample_recognize_pii_entities_with_value_exclusion.py

REQUIRED ENV VARS:
    AZURE_TEXT_ENDPOINT
"""

# [START recognize_pii_entities_with_value_exclusion]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextPiiResult,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiActionContent,
    TextPiiEntitiesRecognitionInput,
    ValueExclusionPolicy,
)


def sample_recognize_pii_entities_with_value_exclusion():
    client = TextAnalysisClient(
        endpoint=os.environ["AZURE_TEXT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    body = TextPiiEntitiesRecognitionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[
                MultiLanguageInput(
                    id="A",
                    text="My name is John Doe and my SSN is 123-45-6789.",
                    language="en",
                )
            ]
        ),
        action_content=PiiActionContent(
            value_exclusion_policy=ValueExclusionPolicy(
                case_sensitive=False,
                excluded_values=["John Doe"],
            )
        ),
    )

    result = client.analyze_text(body=body)
    if isinstance(result, AnalyzeTextPiiResult) and result.results:
        for document in result.results.documents:
            print(f"Redacted text: {document.redacted_text}")
            for entity in document.entities:
                print(f"{entity.text}: {entity.category} ({entity.confidence_score})")


# [END recognize_pii_entities_with_value_exclusion]


if __name__ == "__main__":
    sample_recognize_pii_entities_with_value_exclusion()
