# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_model_evaluation_summary.py
DESCRIPTION:
    This sample demonstrates how to retrieve the evaluation summary for a trained model
    in a Conversation Authoring project.
USAGE:
    python sample_get_model_evaluation_summary.py

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

# [START conversation_authoring_get_model_evaluation_summary]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_get_model_evaluation_summary():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # get evaluation summary for a trained model
    eval_summary = project_client.trained_model.get_model_evaluation_summary(trained_model_label)

    print("=== Model Evaluation Summary ===")

    # ----- Entities evaluation -----
    if eval_summary.entities_evaluation:
        entities_eval = eval_summary.entities_evaluation
        print(
            f"Entities - Micro F1: {entities_eval.micro_f1}, Precision: {entities_eval.micro_precision}, Recall: {entities_eval.micro_recall}"
        )
        print(
            f"Entities - Macro F1: {entities_eval.macro_f1}, Precision: {entities_eval.macro_precision}, Recall: {entities_eval.macro_recall}"
        )

        for name, summary in (entities_eval.entities or {}).items():
            print(f"Entity '{name}': F1 = {summary.f1}, Precision = {summary.precision}, Recall = {summary.recall}")
            print(
                f"  TP: {summary.true_positive_count}, TN: {summary.true_negative_count}, FP: {summary.false_positive_count}, FN: {summary.false_negative_count}"
            )

    # ----- Intents evaluation -----
    if eval_summary.intents_evaluation:
        intents_eval = eval_summary.intents_evaluation
        print(
            f"Intents - Micro F1: {intents_eval.micro_f1}, Precision: {intents_eval.micro_precision}, Recall: {intents_eval.micro_recall}"
        )
        print(
            f"Intents - Macro F1: {intents_eval.macro_f1}, Precision: {intents_eval.macro_precision}, Recall: {intents_eval.macro_recall}"
        )

        for name, summary in (intents_eval.intents or {}).items():
            print(f"Intent '{name}': F1 = {summary.f1}, Precision = {summary.precision}, Recall = {summary.recall}")
            print(
                f"  TP: {summary.true_positive_count}, TN: {summary.true_negative_count}, FP: {summary.false_positive_count}, FN: {summary.false_negative_count}"
            )

# [END conversation_authoring_get_model_evaluation_summary]


def main():
    sample_get_model_evaluation_summary()


if __name__ == "__main__":
    main()
