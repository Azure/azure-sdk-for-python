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
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME   # defaults to "<project-name>"
    (Optional) TRAINED_MODEL  # defaults to "<trained-model-label>"
"""

# [START conversation_authoring_get_model_evaluation_summary_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

async def sample_get_model_evaluation_summary_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        # get evaluation summary for a trained model
        eval_summary = await project_client.trained_model.get_model_evaluation_summary(trained_model_label)

        print("=== Model Evaluation Summary ===")

        # ----- Entities evaluation -----
        entities_eval = getattr(eval_summary, "entities_evaluation", None)
        if entities_eval:
            print(f"Entities - Micro F1: {entities_eval.micro_f1}, Precision: {entities_eval.micro_precision}, Recall: {entities_eval.micro_recall}")
            print(f"Entities - Macro F1: {entities_eval.macro_f1}, Precision: {entities_eval.macro_precision}, Recall: {entities_eval.macro_recall}")

            for name, summary in (entities_eval.entities or {}).items():
                print(f"Entity '{name}': F1 = {summary.f1}, Precision = {summary.precision}, Recall = {summary.recall}")
                print(f"  TP: {summary.true_positive_count}, TN: {summary.true_negative_count}, FP: {summary.false_positive_count}, FN: {summary.false_negative_count}")

        # ----- Intents evaluation -----
        intents_eval = getattr(eval_summary, "intents_evaluation", None)
        if intents_eval:
            print(f"Intents - Micro F1: {intents_eval.micro_f1}, Precision: {intents_eval.micro_precision}, Recall: {intents_eval.micro_recall}")
            print(f"Intents - Macro F1: {intents_eval.macro_f1}, Precision: {intents_eval.macro_precision}, Recall: {intents_eval.macro_recall}")

            for name, summary in (intents_eval.intents or {}).items():
                print(f"Intent '{name}': F1 = {summary.f1}, Precision = {summary.precision}, Recall = {summary.recall}")
                print(f"  TP: {summary.true_positive_count}, TN: {summary.true_negative_count}, FP: {summary.false_positive_count}, FN: {summary.false_negative_count}")
    finally:
        await client.close()

async def main():
    await sample_get_model_evaluation_summary_async()

if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_get_model_evaluation_summary_async]
