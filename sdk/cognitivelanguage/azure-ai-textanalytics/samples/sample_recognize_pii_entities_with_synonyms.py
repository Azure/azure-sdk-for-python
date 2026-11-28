# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_recognize_pii_entities_with_synonyms.py

DESCRIPTION:
    This sample demonstrates how to provide custom context synonyms for PII entity recognition.

USAGE:
    python sample_recognize_pii_entities_with_synonyms.py

REQUIRED ENV VARS:
    AZURE_TEXT_ENDPOINT
"""

# [START recognize_pii_entities_with_synonyms]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    AnalyzeTextPiiResult,
    EntitySynonym,
    EntitySynonyms,
    MultiLanguageInput,
    MultiLanguageTextInput,
    PiiActionContent,
    TextPiiEntitiesRecognitionInput,
)


def sample_recognize_pii_entities_with_synonyms():
    client = TextAnalysisClient(
        endpoint=os.environ["AZURE_TEXT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    entity_synonyms = EntitySynonyms(
        entity_type="USBankAccountNumber",
        synonyms=[
            EntitySynonym(synonym="BANK", language="en"),
            EntitySynonym(synonym="BAN", language="en"),
        ],
    )
    body = TextPiiEntitiesRecognitionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text="My BANK is 123456789.", language="en")]
        ),
        action_content=PiiActionContent(entity_synonyms=[entity_synonyms]),
    )

    result = client.analyze_text(body=body)
    if isinstance(result, AnalyzeTextPiiResult) and result.results:
        for document in result.results.documents:
            for entity in document.entities:
                print(f"{entity.text}: {entity.category} ({entity.confidence_score})")


# [END recognize_pii_entities_with_synonyms]


if __name__ == "__main__":
    sample_recognize_pii_entities_with_synonyms()
