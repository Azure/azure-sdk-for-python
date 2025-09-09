# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_actions.py

DESCRIPTION:
    This sample demonstrates running multiple **text analysis actions** in a single job:
    - Named Entity Recognition
    - Key Phrase Extraction

USAGE:
    python sample_analyze_actions.py

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

# [START analyze]
import os

from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    EntitiesLROTask,
    KeyPhraseLROTask,
    EntityRecognitionOperationResult,
    KeyPhraseExtractionOperationResult,
    EntityTag,
)


def sample_analyze():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    text_a = (
        "We love this trail and make the trip every year. The views are breathtaking and well worth the hike!"
        " Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was"
        " amazing. Everyone in my family liked the trail although it was too challenging for the less"
        " athletic among us. Not necessarily recommended for small children. A hotel close to the trail"
        " offers services for childcare in case you want that."
    )

    text_b = (
        "Sentences in different languages."
    )

    text_c = (
        "That was the best day of my life! We went on a 4 day trip where we stayed at Hotel Foo. They had"
        " great amenities that included an indoor pool, a spa, and a bar. The spa offered couples massages"
        " which were really good. The spa was clean and felt very peaceful. Overall the whole experience was"
        " great. We will definitely come back."
    )

    text_d = ""

    # Prepare documents (you can batch multiple docs)
    text_input = MultiLanguageTextInput(
        multi_language_inputs=[
            MultiLanguageInput(id="A", text=text_a, language="en"),
            MultiLanguageInput(id="B", text=text_b, language="es"),
            MultiLanguageInput(id="C", text=text_c, language="en"),
            MultiLanguageInput(id="D", text=text_d),
        ]
    )

    actions = [
        EntitiesLROTask(name="EntitiesOperationActionSample"),
        KeyPhraseLROTask(name="KeyPhraseOperationActionSample"),
    ]

    # Submit a multi-action analysis job (LRO)
    poller = client.begin_analyze_text_job(text_input=text_input, actions=actions)
    paged_actions = poller.result()

    # Iterate through each action's results
    for action_result in paged_actions:
        print()  # spacing between action blocks

        # --- Entities ---
        if isinstance(action_result, EntityRecognitionOperationResult):
            print("=== Entity Recognition Results ===")
            for ent_doc in action_result.results.documents:
                print(f'Result for document with Id = "{ent_doc.id}":')
                print(f"  Recognized {len(ent_doc.entities)} entities:")
                for entity in ent_doc.entities:
                    print(f"    Text: {entity.text}")
                    print(f"    Offset: {entity.offset}")
                    print(f"    Length: {entity.length}")
                    print(f"    Category: {entity.category}")
                    if hasattr(entity, "type") and entity.type is not None:
                        print(f"    Type: {entity.type}")
                    if hasattr(entity, "subcategory") and entity.subcategory:
                        print(f"    Subcategory: {entity.subcategory}")
                    if hasattr(entity, "tags") and entity.tags:
                        print("    Tags:")
                        for tag in entity.tags:
                            if isinstance(tag, EntityTag):
                                print(f"        TagName: {tag.name}")
                                print(f"        TagConfidenceScore: {tag.confidence_score}")
                    print(f"    Confidence score: {entity.confidence_score}")
                    print()
            for err in action_result.results.errors:
                print(f'  Error in document: {err.id}!')
                print(f"  Document error: {err.error}")

        # --- Key Phrases ---
        elif isinstance(action_result, KeyPhraseExtractionOperationResult):
            print("=== Key Phrase Extraction Results ===")
            for kp_doc in action_result.results.documents:
                print(f'Result for document with Id = "{kp_doc.id}":')
                for kp in kp_doc.key_phrases:
                    print(f"    {kp}")
                print()
            for err in action_result.results.errors:
                print(f'  Error in document: {err.id}!')
                print(f"  Document error: {err.error}")

# [END analyze]


def main():
    sample_analyze()


if __name__ == "__main__":
    main()
