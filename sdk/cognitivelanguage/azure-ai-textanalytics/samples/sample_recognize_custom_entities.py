# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_text_custom_entities.py

DESCRIPTION:
    This sample demonstrates how to run a **custom entity recognition** action over text.

USAGE:
    python sample_text_custom_entities.py

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

# [START text_custom_entities]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    AnalyzeTextOperationAction,
    CustomEntitiesActionContent,
    CustomEntitiesLROTask,
    CustomEntityRecognitionOperationResult,
)


def sample_text_custom_entities():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = os.environ.get("DEPLOYMENT_NAME", "<deployment-name>")

    credential = DefaultAzureCredential()
    client = TextAnalysisClient(endpoint, credential=credential)

    # input
    text_a = (
        "We love this trail and make the trip every year. The views are breathtaking and well worth the hike! "
        "Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was amazing."
    )
    text_input = MultiLanguageTextInput(
        multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
    )

    action_content = CustomEntitiesActionContent(
        project_name=project_name,
        deployment_name=deployment_name,
    )
    actions: list[AnalyzeTextOperationAction] = [
        CustomEntitiesLROTask(name="Custom Entities", parameters=action_content)
    ]

    # LRO
    poller = client.begin_analyze_text_job(text_input=text_input, actions=actions)

    print(f"Operation ID: {poller.details.get('operation_id')}")
    paged_actions = poller.result()

    d = poller.details
    print(f"Job ID: {d.get('job_id')}")
    print(f"Status: {d.get('status')}")
    print(f"Created: {d.get('created_date_time')}")
    print(f"Last Updated: {d.get('last_updated_date_time')}")
    if d.get("expiration_date_time"):
        print(f"Expires: {d.get('expiration_date_time')}")
    if d.get("display_name"):
        print(f"Display Name: {d.get('display_name')}")

    for actions_page in paged_actions:
        print(
            f"Completed: {actions_page.completed}, In Progress: {actions_page.in_progress}, "
            f"Failed: {actions_page.failed}, Total: {actions_page.total}"
        )
        for op_result in actions_page.items_property or []:
            if isinstance(op_result, CustomEntityRecognitionOperationResult):
                print(f"\nAction Name: {op_result.task_name}")
                print(f"Action Status: {op_result.status}")
                print(f"Kind: {op_result.kind}")
                for doc in (op_result.results.documents or []):
                    print(f"Document ID: {doc.id}")
                    for entity in (doc.entities or []):
                        print(f"  Text: {entity.text}")
                        print(f"  Category: {entity.category}")
                        print(f"  Offset: {entity.offset}, Length: {entity.length}")
                        print(f"  Confidence score: {entity.confidence_score}\n")

# [END text_custom_entities]


def main():
    sample_text_custom_entities()


if __name__ == "__main__":
    main()
