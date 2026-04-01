# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities_with_redaction_policies.py

DESCRIPTION:
    This sample demonstrates how to run **PII entity recognition** with redaction policies,
    including synthetic replacement for selected PII categories.

USAGE:
    python sample_recognize_pii_entities_with_redaction_policies.py

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

# [START recognize_pii_entities_with_redaction_policies]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageInput,
    MultiLanguageTextInput,
    TextPiiEntitiesRecognitionInput,
    PiiActionContent,
    EntityMaskPolicyType,
    CharacterMaskPolicyType,
    SyntheticReplacementPolicyType,
    AnalyzeTextPiiResult,
)


def sample_pii_with_redaction_policies():
    # Settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # Input text
    text_1 = "My name is John Doe. My SSN is 123-45-6789. My email is john@example.com."
    text_2 = "Contact John Doe at john@example.com. SSN: 123-45-6789."

    body = TextPiiEntitiesRecognitionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[
                MultiLanguageInput(id="1", text=text_1, language="en"),
                MultiLanguageInput(id="2", text=text_2, language="en"),
            ]
        ),
        action_content=PiiActionContent(
            pii_categories=["All"],
            redaction_policies=[
                # Default policy: mask all PII categories (asterisks)
                EntityMaskPolicyType(policy_name="defaultPolicy", is_default=True),
                # For SSN: only mask characters except first 4 digits
                CharacterMaskPolicyType(
                    policy_name="ssnMaskPolicy",
                    unmask_length=4,
                    unmask_from_end=False,
                    entity_types=["USSocialSecurityNumber"],
                ),
                # For Person & Email: replace with synthetic data (fake names/emails)
                SyntheticReplacementPolicyType(
                    policy_name="syntheticPolicy",
                    entity_types=["Person", "Email"],
                ),
            ],
        ),
    )

    # Sync call
    result = client.analyze_text(body=body)

    # Display results
    if isinstance(result, AnalyzeTextPiiResult) and result.results:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            print(f"Redacted Text:\n  {doc.redacted_text}\n")

            print("Detected Entities:")
            for entity in doc.entities or []:
                print(f"  Text: {entity.text}")
                print(f"  Category: {entity.category}")
                print(f"  Masked As: {entity.mask}")
                print(f"  Confidence: {entity.confidence_score}")
                print("")
    else:
        print("No results returned or unexpected result type.")


# [END recognize_pii_entities_with_redaction_policies]


def main():
    sample_pii_with_redaction_policies()


if __name__ == "__main__":
    main()
