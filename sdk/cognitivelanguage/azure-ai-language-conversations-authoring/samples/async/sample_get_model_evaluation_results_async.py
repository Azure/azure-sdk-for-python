# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_model_evaluation_results_async.py
DESCRIPTION:
    This sample demonstrates how to retrieve detailed evaluation results (per utterance)
    for a trained model in a Conversation Authoring project (async).
USAGE:
    python sample_get_model_evaluation_results_async.py
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME       # defaults to "<project-name>"
    (Optional) TRAINED_MODEL      # defaults to "<trained-model-label>"
"""

# [START conversation_authoring_get_model_evaluation_results_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient


async def sample_get_model_evaluation_results_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        # fetch async paged evaluation results
        results = await project_client.trained_model.get_model_evaluation_results(
            trained_model_label=trained_model_label, string_index_type="Utf16CodeUnit"
        )

        print("=== Model Evaluation Results ===")
        seen = 0
        async for r in results:
            seen += 1
            print(f"Text: {getattr(r, 'text', None)}")
            print(f"Language: {getattr(r, 'language', None)}")

            intents_result = getattr(r, "intents_result", None)
            if intents_result:
                print(f"Expected Intent: {getattr(intents_result, 'expected_intent', None)}")
                print(f"Predicted Intent: {getattr(intents_result, 'predicted_intent', None)}")

            entities_result = getattr(r, "entities_result", None)
            if entities_result:
                expected_entities = getattr(entities_result, "expected_entities", []) or []
                print("Expected Entities:")
                for ent in expected_entities:
                    print(f" - Category: {ent.category}, Offset: {ent.offset}, Length: {ent.length}")

                predicted_entities = getattr(entities_result, "predicted_entities", []) or []
                print("Predicted Entities:")
                for ent in predicted_entities:
                    print(f" - Category: {ent.category}, Offset: {ent.offset}, Length: {ent.length}")

            print()

        print(f"Total Results: {seen}")
    finally:
        await client.close()


async def main():
    await sample_get_model_evaluation_results_async()


if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_get_model_evaluation_results_async]
