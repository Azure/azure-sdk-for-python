# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_text_custom_multi_label_classification_async.py

DESCRIPTION:
    This sample demonstrates how to run a **custom multi-label classification** action over text (async LRO).

USAGE:
    python sample_text_custom_multi_label_classification_async.py

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

# [START text_custom_multi_label_classification_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.textanalytics.aio import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    CustomMultiLabelClassificationActionContent,
    CustomMultiLabelClassificationOperationAction,
    CustomMultiLabelClassificationOperationResult,
)


async def sample_text_custom_multi_label_classification_async():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = os.environ.get("DEPLOYMENT_NAME", "<deployment-name>")

    credential = DefaultAzureCredential()

    async with TextAnalysisClient(endpoint, credential=credential) as client:
        # Build input
        text_a = (
            "I need a reservation for an indoor restaurant in China. Please don't stop the music. "
            "Play music and add it to my playlist."
        )

        text_input = MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        )

        action = CustomMultiLabelClassificationOperationAction(
            name="Custom Multi-Label Classification",
            action_content=CustomMultiLabelClassificationActionContent(
                project_name=project_name,
                deployment_name=deployment_name,
            ),
        )

        # Start long-running operation (async)
        poller = await client.begin_analyze_text_job(
            text_input=text_input,
            actions=[action],
        )

        # Operation metadata (pre-final)
        print(f"Operation ID: {poller.details.get('operation_id')}")

        # Wait for completion and get AsyncItemPaged of TextActions
        paged_actions = await poller.result()

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
        if d.get("errors"):
            print("\nErrors:")
            for err in d["errors"]:
                print(f"  Code: {err.code} - {err.message}")

        # Iterate results (async pageable)
        async for actions_page in paged_actions:
            # Page-level counts if available
            print(
                f"Completed: {actions_page.completed}, "
                f"In Progress: {actions_page.in_progress}, "
                f"Failed: {actions_page.failed}, "
                f"Total: {actions_page.total}"
            )

            # Items are the individual operation results
            for op_result in actions_page.items_property or []:
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
                else:
                    try:
                        print(
                            f"\n[Other action] name={op_result.task_name}, "
                            f"status={op_result.status}, kind={op_result.kind}"
                        )
                    except Exception:
                        print("\n[Other action present]")


# [END text_custom_multi_label_classification_async]


async def main():
    await sample_text_custom_multi_label_classification_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
