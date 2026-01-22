# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities_with_redaction_policies_async.py

DESCRIPTION:
    This sample demonstrates how to run **PII entity recognition** with redaction policies (async),
    including synthetic replacement for selected PII categories.

USAGE:
    python sample_recognize_pii_entities_with_redaction_policies_async.py

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

# [START recognize_pii_entities_with_redaction_policies_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
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


async def sample_recognize_pii_entities_with_redaction_policies_async():
    # Settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    async with TextAnalysisClient(endpoint, credential=credential) as client:
        # Input
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
                    # Default policy: mask all categories (asterisks)
                    EntityMaskPolicyType(policy_name="defaultPolicy", is_default=True),
                    # SSN: keep first 4 characters visible, mask the rest
                    CharacterMaskPolicyType(
                        policy_name="ssnMaskPolicy",
                        unmask_length=4,
                        unmask_from_end=False,
                        entity_types=["USSocialSecurityNumber"],
                    ),
                    # Person & Email: replace with synthetic (fake) values
                    SyntheticReplacementPolicyType(
                        policy_name="syntheticPolicy",
                        entity_types=["Person", "Email"],
                    ),
                ],
            ),
        )

        # Async (non-LRO) call
        result = await client.analyze_text(body=body)

        # Print results
        if isinstance(result, AnalyzeTextPiiResult) and result.results:
            for doc in result.results.documents:
                print(f"\nDocument ID: {doc.id}")
                print(f"Redacted Text:\n  {doc.redacted_text}\n")

                if doc.entities:
                    print("Detected Entities:")
                    for entity in doc.entities:
                        print(f"  Text: {entity.text}")
                        print(f"  Category: {entity.category}")
                        if entity.subcategory:
                            print(f"  Subcategory: {entity.subcategory}")
                        print(f"  Masked As: {entity.mask}")
                        print(f"  Offset: {entity.offset}")
                        print(f"  Length: {entity.length}")
                        print(f"  Confidence score: {entity.confidence_score}\n")
                else:
                    print("No PII entities found for this document.")
        else:
            print("No documents in the response or unexpected result type.")


# [END recognize_pii_entities_with_redaction_policies_async]


async def main():
    await sample_recognize_pii_entities_with_redaction_policies_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
