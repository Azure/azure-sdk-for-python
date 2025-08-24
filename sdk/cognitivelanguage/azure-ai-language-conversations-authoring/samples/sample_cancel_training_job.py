# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_cancel_training_job.py
DESCRIPTION:
    This sample demonstrates how to cancel a training job in a Conversation Authoring project.
USAGE:
    python sample_cancel_training_job.py

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

# [START conversation_authoring_cancel_training_job]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_cancel_training_job():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    job_id = os.environ.get("JOB_ID", "<job-id>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    captured = {}

    def capture_initial_response(pipeline_response):
        # capture the raw HTTP response without polling
        http_resp = pipeline_response.http_response
        captured["status_code"] = http_resp.status_code
        captured["headers"] = http_resp.headers

    # send cancel request (no polling)
    poller = project_client.project.begin_cancel_training_job(
        job_id=job_id,
        polling=False,
        raw_response_hook=capture_initial_response,
    )

    # check initial status
    status = captured.get("status_code")
    print(f"Cancel Training Job Response Status: {status}")

    # print headers (polling endpoints)
    headers = captured.get("headers", {}) or {}
    print(f"Operation-Location: {headers.get('Operation-Location') or headers.get('operation-location')}")
    print(f"Location: {headers.get('Location') or headers.get('location')}")

# [END conversation_authoring_cancel_training_job]


def main():
    sample_cancel_training_job()


if __name__ == "__main__":
    main()
