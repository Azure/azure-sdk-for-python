# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities_with_confidence_score.py

DESCRIPTION:
    This sample demonstrates how to run **PII entity recognition** with confidence score
    thresholds, including entity-specific overrides.

USAGE:
    python sample_recognize_pii_entities_with_confidence_score.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you prefer to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
"""

# [START recognize_pii_entities_with_confidence_score]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageInput,
    MultiLanguageTextInput,
    TextPiiEntitiesRecognitionInput,
    PiiActionContent,
    ConfidenceScoreThreshold,
    ConfidenceScoreThresholdOverride,
    AnalyzeTextPiiResult,
)


def sample_recognize_pii_entities_with_confidence_score():
    # Settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # Input text
    text = "My name is John Doe. My SSN is 222-45-6789. My email is john@example.com. " "John Doe is my name."

    # Confidence score threshold configuration:
    # - Default threshold is 0.3
    # - SSN & Email require 0.9 minimum confidence to be returned
    threshold = ConfidenceScoreThreshold(
        default=0.3,
        overrides=[
            ConfidenceScoreThresholdOverride(value=0.9, entity="USSocialSecurityNumber"),
            ConfidenceScoreThresholdOverride(value=0.9, entity="Email"),
        ],
    )

    body = TextPiiEntitiesRecognitionInput(
        text_input=MultiLanguageTextInput(multi_language_inputs=[MultiLanguageInput(id="1", text=text, language="en")]),
        action_content=PiiActionContent(
            pii_categories=["All"],
            disable_entity_validation=True,
            confidence_score_threshold=threshold,
        ),
    )

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextPiiResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            print(f"Redacted Text:\n  {doc.redacted_text}\n")

            print("Detected Entities (after threshold filtering):")
            if doc.entities:
                for entity in doc.entities:
                    print(f"  Text: {entity.text}")
                    print(f"  Category: {entity.category}")
                    print(f"  Masked As: {entity.mask}")
                    print(f"  Confidence score: {entity.confidence_score}\n")
            else:
                print("  No entities met the confidence threshold.")
    else:
        print("No documents in the response or unexpected result type.")


# [END recognize_pii_entities_with_confidence_score]


def main():
    sample_recognize_pii_entities_with_confidence_score()


if __name__ == "__main__":
    main()
