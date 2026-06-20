# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_single_label_classify.py

DESCRIPTION:
    This sample demonstrates how to run a **custom single-label classification** action over text.

USAGE:
    python sample_single_label_classify.py

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

# [START text_custom_single_label_classification]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    CustomSingleLabelClassificationActionContent,
    CustomSingleLabelClassificationOperationAction,
    CustomSingleLabelClassificationOperationResult,
)


def sample_single_label_classify():
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

    action = CustomSingleLabelClassificationOperationAction(
        name="Custom Single-Label Classification",
        action_content=CustomSingleLabelClassificationActionContent(
            project_name=project_name,
            deployment_name=deployment_name,
        ),
    )

    # Start long-running operation (sync)
    poller = client.begin_analyze_text_job(
        text_input=text_input,
        actions=[action],
    )

    # Operation metadata (pre-final)
    print(f"Operation ID: {poller.details.get('operation_id')}")

    # Wait for completion and get pageable of TextActions
    paged_actions = poller.result()

    # Final-state metadata
    d = poller.details
    print(f"Job ID: {d.get('job_id')}")
    print(f"Status: {d.get('status')}")
    print(f"Created: {d.get('created_date_time')}")
    print(f"Last Updated: {d.get('last_updated_date_time')}")
    if d.get("expiration_date_time"):
        print(f"Expires: {d.get('expiration_date_time')}")
    if d.get("display_name"):
        print(f"Display Name: {d.get('display_name')}")

    # Iterate results (sync pageable)
    for actions_page in paged_actions:
        # Page-level counts (if available)
        print(
            f"Completed: {actions_page.completed}, "
            f"In Progress: {actions_page.in_progress}, "
            f"Failed: {actions_page.failed}, "
            f"Total: {actions_page.total}"
        )

        # Items are the individual operation results
        for op_result in actions_page.items_property or []:
            if isinstance(op_result, CustomSingleLabelClassificationOperationResult):
                print(f"\nAction Name: {op_result.task_name}")
                print(f"Action Status: {op_result.status}")
                print(f"Kind: {op_result.kind}")

                result = op_result.results
                for doc in result.documents or []:
                    print(f"\nDocument ID: {doc.id}")
                    # Single-label: typically one class, but iterate to be general
                    for cls_item in doc.class_property or []:
                        print(f"  Predicted category: {cls_item.category}")
                        print(f"  Confidence score: {cls_item.confidence_score}")
            else:
                # Other action kinds, if present
                try:
                    print(
                        f"\n[Non-CSC action] name={op_result.task_name}, "
                        f"status={op_result.status}, kind={op_result.kind}"
                    )
                except (AttributeError, TypeError) as e:
                    print(f"\n[Non-CSC action present] Error: {e}")


# [END text_custom_single_label_classification]


def main():
    sample_single_label_classify()


if __name__ == "__main__":
    main()
