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
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME   # defaults to "<project-name>"
    (Optional) JOB_ID         # defaults to "<job-id>"
"""

# [START conversation_authoring_cancel_training_job_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

async def sample_cancel_training_job_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    job_id = os.environ.get("JOB_ID", "<job-id>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        captured = {}

        def capture_initial_response(pipeline_response):
            http_resp = pipeline_response.http_response
            captured["status_code"] = http_resp.status_code
            captured["headers"] = http_resp.headers

        # send cancel request (no polling)
        poller = await project_client.project.begin_cancel_training_job(
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

        # you still have a poller object (NoPolling)
        assert poller is not None
    finally:
        await client.close()

async def main():
    await sample_cancel_training_job_async()

if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_cancel_training_job_async]
