# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_train.py
DESCRIPTION:
    This sample demonstrates how to start a training job for a Conversation Authoring project
    and print the final training result.
USAGE:
    python sample_train.py

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

# [START conversation_authoring_train]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    TrainingJobDetails,
    TrainingMode,
    EvaluationDetails,
    EvaluationKind,
)


def sample_train():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # build training request
    training_job_details = TrainingJobDetails(
        model_label="<model-label>",
        training_mode=TrainingMode.STANDARD,
        training_config_version="<config-version>",
        evaluation_options=EvaluationDetails(
            kind=EvaluationKind.PERCENTAGE,
            testing_split_percentage=20,
            training_split_percentage=80,
        ),
    )

    # start training job (long-running operation)
    poller = project_client.project.begin_train(body=training_job_details)

    # wait for job completion and get the result (no explicit type variables)
    result = poller.result()

    # print result details
    print("=== Training Result ===")
    print(f"Model Label: {result.model_label}")
    print(f"Training Config Version: {result.training_config_version}")
    print(f"Training Mode: {result.training_mode}")
    print(f"Training Status: {result.training_status}")
    print(f"Data Generation Status: {result.data_generation_status}")
    print(f"Evaluation Status: {result.evaluation_status}")
    print(f"Estimated End: {result.estimated_end_on}")


# [END conversation_authoring_train]


def main():
    sample_train()


if __name__ == "__main__":
    main()
