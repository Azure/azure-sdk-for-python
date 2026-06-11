# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_model_evaluation_results.py
DESCRIPTION:
    This sample demonstrates how to retrieve detailed evaluation results (per utterance)
    for a trained model in a Conversation Authoring project.
USAGE:
    python sample_get_model_evaluation_results.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
      - AZURE_CONVERSATIONS_AUTHORING_KEY

OPTIONAL ENV VARS:
    PROJECT_NAME       # defaults to "<project-name>"
    TRAINED_MODEL      # defaults to "<trained-model-label>"
"""

# [START conversation_authoring_get_model_evaluation_results]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_get_model_evaluation_results():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # fetch paged evaluation results
    results = project_client.trained_model.get_model_evaluation_results(
        trained_model_label=trained_model_label, string_index_type="Utf16CodeUnit"
    )

    print("=== Model Evaluation Results ===")
    seen = 0
    for r in results:
        seen += 1
        print(f"Text: {r.text}")
        print(f"Language: {r.language}")

        if r.intents_result:
            print(f"Expected Intent: {r.intents_result.expected_intent}")
            print(f"Predicted Intent: {r.intents_result.predicted_intent}")

        if r.entities_result:
            expected_entities = r.entities_result.expected_entities or []
            print("Expected Entities:")
            for ent in expected_entities:
                print(f" - Category: {ent.category}, Offset: {ent.offset}, Length: {ent.length}")

            predicted_entities = r.entities_result.predicted_entities or []
            print("Predicted Entities:")
            for ent in predicted_entities:
                print(f" - Category: {ent.category}, Offset: {ent.offset}, Length: {ent.length}")

        print()

    print(f"Total Results: {seen}")


# [END conversation_authoring_get_model_evaluation_results]


def main():
    sample_get_model_evaluation_results()


if __name__ == "__main__":
    main()
