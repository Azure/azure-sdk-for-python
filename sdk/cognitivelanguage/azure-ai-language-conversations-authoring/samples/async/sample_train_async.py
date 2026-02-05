# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_train_async.py
DESCRIPTION:
    This sample demonstrates how to start a training job for a Conversation Authoring project (async)
    and print the final training result.
USAGE:
    python sample_train_async.py

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
    PROJECT_NAME  # defaults to "<project-name>"
"""

# [START conversation_authoring_train_async]
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    TrainingJobDetails,
    TrainingMode,
    EvaluationDetails,
    EvaluationKind,
)


async def sample_train_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # async client with AAD
    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        project_client = client.get_project_client(project_name)

        # build training request
        details = TrainingJobDetails(
            model_label="<model-label>",
            training_mode=TrainingMode.STANDARD,
            training_config_version="<config-version>",
            evaluation_options=EvaluationDetails(
                kind=EvaluationKind.PERCENTAGE,
                testing_split_percentage=20,
                training_split_percentage=80,
            ),
        )

        # start training job (async long-running operation)
        poller = await project_client.project.begin_train(body=details)

        # wait for job completion and get the result (no explicit type variables)
        result = await poller.result()

        # print result details (direct attribute access; no getattr)
        print("=== Training Result ===")
        print(f"Model Label: {result.model_label}")
        print(f"Training Config Version: {result.training_config_version}")
        print(f"Training Mode: {result.training_mode}")
        print(f"Training Status: {result.training_status}")
        print(f"Data Generation Status: {result.data_generation_status}")
        print(f"Evaluation Status: {result.evaluation_status}")
        print(f"Estimated End: {result.estimated_end_on}")


# [END conversation_authoring_train_async]


async def main():
    await sample_train_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
