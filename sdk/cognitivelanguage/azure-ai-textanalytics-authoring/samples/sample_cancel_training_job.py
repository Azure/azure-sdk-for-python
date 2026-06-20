# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_cancel_training_job.py
DESCRIPTION:
    This sample demonstrates how to cancel a running **Text Authoring** training job.
USAGE:
    python sample_cancel_training_job.py
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
    PROJECT_NAME       # defaults to "<project-name>"
    TRAINING_JOB_ID    # defaults to "<training-job-id>"
"""

# [START text_authoring_cancel_training_job]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient


def sample_cancel_training_job():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    job_id = os.environ.get("TRAINING_JOB_ID", "<training-job-id>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # project-scoped client
    project_client = client.get_project_client(project_name)

    # cancel the training job (LRO)
    poller = project_client.project.begin_cancel_training_job(job_id=job_id)
    result = poller.result()  # TrainingJobResult

    # print important fields (direct attribute access; no getattr)
    print("=== Cancel Training Job Result ===")
    print(f"Model Label: {result.model_label}")
    print(f"Training Config Version: {result.training_config_version}")
    if result.training_status is not None:
        print(f"Training Status: {result.training_status.status}")
        print(f"Training %: {result.training_status.percent_complete}")
    if result.evaluation_status is not None:
        print(f"Evaluation Status: {result.evaluation_status.status}")
        print(f"Evaluation %: {result.evaluation_status.percent_complete}")
    print(f"Estimated End: {result.estimated_end_on}")


# [END text_authoring_cancel_training_job]


def main():
    sample_cancel_training_job()


if __name__ == "__main__":
    main()
