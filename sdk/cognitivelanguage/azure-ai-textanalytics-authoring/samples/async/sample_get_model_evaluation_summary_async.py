# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_model_evaluation_summary_async.py
DESCRIPTION:
    This sample demonstrates how to get a **model evaluation summary** for a trained model
    in a Text Authoring project (overall metrics + class metrics + confusion matrix) — async version.
USAGE:
    python sample_get_model_evaluation_summary_async.py
REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
OPTIONAL ENV VARS:
    PROJECT_NAME         # defaults to "<project-name>"
    TRAINED_MODEL_LABEL  # defaults to "<trained-model-label>"
"""

# [START text_authoring_get_model_evaluation_summary_async]
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CustomSingleLabelClassificationEvalSummary,
)


async def sample_get_model_evaluation_summary_async():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL_LABEL", "<trained-model-label>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    async with TextAuthoringClient(endpoint, credential=credential) as client:
        # trained-model–scoped call
        project_client = client.get_project_client(project_name)
        eval_summary = await project_client.trained_model.get_model_evaluation_summary(trained_model_label)

        print("=== Model Evaluation Summary ===")
        assert isinstance(eval_summary, CustomSingleLabelClassificationEvalSummary)

        # Evaluation options
        evaluation_options = eval_summary.evaluation_options
        print("Evaluation Options:")
        print(f"    Kind: {evaluation_options.kind}")
        print(f"    Training Split Percentage: {evaluation_options.training_split_percentage}")
        print(f"    Testing Split Percentage: {evaluation_options.testing_split_percentage}")

        # Single-label classification evaluation (micro/macro metrics)
        sl_eval = eval_summary.custom_single_label_classification_evaluation
        print(f"Micro F1: {sl_eval.micro_f1}")
        print(f"Micro Precision: {sl_eval.micro_precision}")
        print(f"Micro Recall: {sl_eval.micro_recall}")
        print(f"Macro F1: {sl_eval.macro_f1}")
        print(f"Macro Precision: {sl_eval.macro_precision}")
        print(f"Macro Recall: {sl_eval.macro_recall}")

        # Confusion matrix (dict-of-dicts with normalized/raw values)
        cmatrix = sl_eval.confusion_matrix
        if cmatrix:
            print("Confusion Matrix:")
            for row_key, row_val in cmatrix.items():
                print(f"Row: {row_key}")
                for col_key, cell in row_val.items():
                    print(
                        f"    Column: {col_key}, Normalized Value: {cell['normalizedValue']}, Raw Value: {cell['rawValue']}"
                    )

        # Class-specific metrics
        classes_map = sl_eval.classes
        if classes_map:
            print("Class-Specific Metrics:")
            for cls_name, metrics in classes_map.items():
                print(f"Class: {cls_name}")
                print(f"    F1: {metrics.f1}")
                print(f"    Precision: {metrics.precision}")
                print(f"    Recall: {metrics.recall}")
                print(f"    True Positives: {metrics.true_positive_count}")
                print(f"    True Negatives: {metrics.true_negative_count}")
                print(f"    False Positives: {metrics.false_positive_count}")
                print(f"    False Negatives: {metrics.false_negative_count}")


# [END text_authoring_get_model_evaluation_summary_async]


async def main():
    await sample_get_model_evaluation_summary_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
