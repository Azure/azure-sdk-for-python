# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_multi_label_classify.py

DESCRIPTION:
    This sample demonstrates how to run a **custom multi-label classification** action over text.

USAGE:
    python sample_text_custom_multi_label_classification.py

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
    PROJECT_NAME        # defaults to "<project-name>"
    DEPLOYMENT_NAME     # defaults to "<deployment-name>"
"""

# [START text_custom_multi_label_classification]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    CustomMultiLabelClassificationActionContent,
    CustomMultiLabelClassificationOperationAction,
    CustomMultiLabelClassificationOperationResult,
)


def sample_multi_label_classify():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = os.environ.get("DEPLOYMENT_NAME", "<deployment-name>")
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # Build input
    text_a = (
        "I need a reservation for an indoor restaurant in China. Please don't stop the music. "
        "Play music and add it to my playlist."
    )

    text_input = MultiLanguageTextInput(multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")])

    action = CustomMultiLabelClassificationOperationAction(
        name="Custom Multi-Label Classification",
        action_content=CustomMultiLabelClassificationActionContent(
            project_name=project_name,
            deployment_name=deployment_name,
        ),
    )

    # Start long-running operation (sync)
    poller = client.begin_analyze_text_job(
        text_input=text_input,
        actions=[action],
    )

    job_state = poller.result()
    print(f"Job ID: {job_state.job_id}")
    print(f"Status: {job_state.status}")

    if job_state.actions:
        for op_result in job_state.actions.items_property or []:
            if isinstance(op_result, CustomMultiLabelClassificationOperationResult):
                print(f"\nAction Name: {op_result.task_name}")
                print(f"Action Status: {op_result.status}")
                print(f"Kind: {op_result.kind}")

                results = op_result.results
                for doc in results.documents or []:
                    print(f"\nDocument ID: {doc.id}")
                    print("Predicted Labels:")
                    for cls_item in doc.class_property or []:
                        print(f"  Category: {cls_item.category}")
                        print(f"  Confidence score: {cls_item.confidence_score}")


# [END text_custom_multi_label_classification]


def main():
    sample_multi_label_classify()


if __name__ == "__main__":
    main()
