# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_model_evaluation_summary_async.py
DESCRIPTION:
    This sample demonstrates how to retrieve the evaluation summary for a trained model
    in a Conversation Authoring project (async).
USAGE:
    python sample_get_model_evaluation_summary_async.py

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
    PROJECT_NAME   # defaults to "<project-name>"
    TRAINED_MODEL  # defaults to "<trained-model-label>"
"""

# [START conversation_authoring_get_model_evaluation_summary_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient


async def sample_get_model_evaluation_summary_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        project_client = client.get_project_client(project_name)

        # get evaluation summary for a trained model
        eval_summary = await project_client.trained_model.get_model_evaluation_summary(trained_model_label)

        print("=== Model Evaluation Summary ===")

        # ----- Entities evaluation (micro/macro) -----
        entities_summary = eval_summary.entities_evaluation
        if entities_summary is not None:
            print(
                f"Entities - Micro F1: {entities_summary.micro_f1}, "
                f"Micro Precision: {entities_summary.micro_precision}, "
                f"Micro Recall: {entities_summary.micro_recall}"
            )
            print(
                f"Entities - Macro F1: {entities_summary.macro_f1}, "
                f"Macro Precision: {entities_summary.macro_precision}, "
                f"Macro Recall: {entities_summary.macro_recall}"
            )

            # Per-entity details
            ent_map = entities_summary.entities or {}
            for entity_name, entity_summary in ent_map.items():
                print(
                    f"Entity '{entity_name}': F1 = {entity_summary.f1}, Precision = {entity_summary.precision}, Recall = {entity_summary.recall}"
                )
                print(
                    f"  True Positives: {entity_summary.true_positive_count}, "
                    f"True Negatives: {entity_summary.true_negative_count}"
                )
                print(
                    f"  False Positives: {entity_summary.false_positive_count}, "
                    f"False Negatives: {entity_summary.false_negative_count}"
                )

        # ----- Intents evaluation (micro/macro) -----
        intents_summary = eval_summary.intents_evaluation
        if intents_summary is not None:
            print(
                f"Intents - Micro F1: {intents_summary.micro_f1}, "
                f"Micro Precision: {intents_summary.micro_precision}, "
                f"Micro Recall: {intents_summary.micro_recall}"
            )
            print(
                f"Intents - Macro F1: {intents_summary.macro_f1}, "
                f"Macro Precision: {intents_summary.macro_precision}, "
                f"Macro Recall: {intents_summary.macro_recall}"
            )

            # Per-intent details
            intent_map = intents_summary.intents or {}
            for intent_name, intent_summary in intent_map.items():
                print(
                    f"Intent '{intent_name}': F1 = {intent_summary.f1}, Precision = {intent_summary.precision}, Recall = {intent_summary.recall}"
                )
                print(
                    f"  True Positives: {intent_summary.true_positive_count}, "
                    f"True Negatives: {intent_summary.true_negative_count}"
                )
                print(
                    f"  False Positives: {intent_summary.false_positive_count}, "
                    f"False Negatives: {intent_summary.false_negative_count}"
                )


# [END conversation_authoring_get_model_evaluation_summary_async]


async def main():
    await sample_get_model_evaluation_summary_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
