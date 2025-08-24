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
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME  # defaults to "<project-name>"
"""

# [START conversation_authoring_train_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    TrainingJobDetails,
    TrainingMode,
    EvaluationDetails,
    EvaluationKind,
    TrainingJobResult,
)


async def sample_train_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
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

        # wait for job completion and get the result
        result: TrainingJobResult = await poller.result()

        # print result details
        print("=== Training Result ===")
        print(f"Model Label: {result.model_label}")
        print(f"Training Config Version: {result.training_config_version}")
        print(f"Training Mode: {result.training_mode}")
        print(f"Training Status: {result.training_status}")
        print(f"Data Generation Status: {result.data_generation_status}")
        print(f"Evaluation Status: {result.evaluation_status}")
        print(f"Estimated End: {result.estimated_end_on}")
    finally:
        # close the client
        await client.close()


async def main():
    await sample_train_async()


if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_train_async]
