# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_submit_job_async.py

DESCRIPTION:
    This sample shows how to submit an analyze documents job asynchronously and get the final task results.

USAGE:
    python sample_submit_job_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_DOCUMENTS_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key.
    3) AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION - the source document location.
    4) AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION - the output location.
"""

# [START sample_submit_job_async]
import asyncio


async def sample_submit_job() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.documents.aio import AnalyzeDocumentsClient

    endpoint = os.environ["AZURE_LANGUAGE_DOCUMENTS_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    source_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION"]
    target_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION"]

    client = AnalyzeDocumentsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    async with client:
        poller = await client.begin_submit_job(
            body={
                "displayName": "Document Analysis Sample",
                "analysisInput": {
                    "documents": [
                        {
                            "language": "en",
                            "id": "1",
                            "source": {"location": source_location},
                            "target": {"location": target_location},
                        }
                    ]
                },
                "tasks": [
                    {
                        "kind": "PiiEntityRecognition",
                        "parameters": {
                            "redactionPolicies": [
                                {
                                    "policyName": "defaultPolicy",
                                    "policyKind": "EntityMask",
                                    "isDefault": True,
                                }
                            ]
                        },
                    }
                ],
            },
        )

        print(f"Initial poller status: {poller.status()}")
        print(f"Operation ID: {poller.details['operation_id']}")

        results = await poller.result()

        print(f"Final job ID: {poller.details['job_id']}")
        print(f"Final job status: {poller.details['status']}")

        async for tasks in results:
            print(f"Total tasks: {tasks.total}")
            print(f"Completed tasks: {tasks.completed}")
            print(f"Failed tasks: {tasks.failed}")
            print(f"In-progress tasks: {tasks.in_progress}")

            if tasks.items_property:
                for task_result in tasks.items_property:
                    print(f"Task kind: {task_result.kind}")
                    print(f"Task status: {task_result.status}")


# [END sample_submit_job_async]


async def main():
    await sample_submit_job()


if __name__ == "__main__":
    asyncio.run(main())
