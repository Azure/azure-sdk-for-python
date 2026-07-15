# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_job_state.py

DESCRIPTION:
    This sample shows how to submit an analyze documents job and get its job state.

USAGE:
    python sample_get_job_state.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_DOCUMENTS_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key.
    3) AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION - the source document location.
    4) AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION - the output location.
"""

from urllib.parse import urlparse


# [START sample_get_job_state]
def sample_get_job_state() -> None:
    import os
    from urllib.parse import urlparse
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.documents import AnalyzeDocumentsClient

    endpoint = os.environ["AZURE_LANGUAGE_DOCUMENTS_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    source_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION"]
    target_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION"]

    client = AnalyzeDocumentsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    operation_location = {}

    def raw_response_hook(response):
        operation_location["value"] = response.http_response.headers.get("Operation-Location")

    with client:
        client.begin_submit_job(
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
            raw_response_hook=raw_response_hook,
        )

        parsed = urlparse(operation_location["value"])
        job_id = parsed.path.rstrip("/").split("/")[-1]

        response = client.get_job_state(job_id=job_id)

        print(f"Job ID: {response['jobId']}")
        print(f"Status: {response['status']}")


# [END sample_get_job_state]


if __name__ == "__main__":
    sample_get_job_state()
