# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_cancel_training_job_async.py
DESCRIPTION:
    This sample demonstrates how to cancel a training job in a Conversation Authoring project (async).
USAGE:
    python sample_cancel_training_job_async.py

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
    JOB_ID         # defaults to "<job-id>"
"""

# [START conversation_authoring_cancel_training_job_async]
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient


async def sample_cancel_training_job_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    job_id = os.environ.get("JOB_ID", "<job-id>")

    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        project_client = client.get_project_client(project_name)

        poller = await project_client.project.begin_cancel_training_job(
            job_id=job_id,
        )

        result = await poller.result()  # TrainingJobResult
        print(f"Model Label: {result.model_label}")
        print(f"Training Config Version: {result.training_config_version}")
        print(f"Training Mode: {result.training_mode}")
        if result.data_generation_status is not None:
            print(f"Data Generation Status: {result.data_generation_status.status}")
            print(f"Data Generation %: {result.data_generation_status.percent_complete}")
        if result.training_status is not None:
            print(f"Training Status: {result.training_status.status}")
            print(f"Training %: {result.training_status.percent_complete}")
        if result.evaluation_status is not None:
            print(f"Evaluation Status: {result.evaluation_status.status}")
            print(f"Evaluation %: {result.evaluation_status.percent_complete}")
        print(f"Estimated End: {result.estimated_end_on}")


# [END conversation_authoring_cancel_training_job_async]


async def main():
    await sample_cancel_training_job_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
