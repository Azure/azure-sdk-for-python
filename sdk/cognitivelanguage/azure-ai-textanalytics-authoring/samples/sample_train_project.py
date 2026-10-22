# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_train_project.py
DESCRIPTION:
    This sample demonstrates how to train a **Text Authoring** project.
USAGE:
    python sample_train_project.py
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
    PROJECT_NAME            # defaults to "<project-name>"
    MODEL_LABEL             # defaults to "<model-label>"
    TRAINING_CONFIG_VERSION # defaults to "<training-config-version>"
"""

# [START text_authoring_train_project]
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    TrainingJobDetails,
    EvaluationDetails,
    EvaluationKind,
)


def sample_train_project():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    model_label = os.environ.get("MODEL_LABEL", "<model-label>")
    training_config_version = os.environ.get("TRAINING_CONFIG_VERSION", "<training-config-version>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # project-scoped client
    project_client = client.get_project_client(project_name)

    # build training job details (80/20 split by percentage)
    training_job_details = TrainingJobDetails(
        model_label=model_label,
        training_config_version=training_config_version,
        evaluation_options=EvaluationDetails(
            kind=EvaluationKind.PERCENTAGE,
            testing_split_percentage=20,
            training_split_percentage=80,
        ),
    )

    # begin training (LRO) and handle success/error
    poller = project_client.project.begin_train(body=training_job_details)
    try:
        poller.result()  # completes with None; raises on failure
        print("Train completed.")
        print(f"done: {poller.done()}")
        print(f"status: {poller.status()}")
    except HttpResponseError as e:
        print(f"Operation failed: {e.message}")
        print(e.error)


# [END text_authoring_train_project]


def main():
    sample_train_project()


if __name__ == "__main__":
    main()
