# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_submit_job.py

DESCRIPTION:
    This sample shows how to submit an analyze documents job.

USAGE:
    python sample_submit_job.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_DOCUMENTS_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key.
    3) AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION - the source document location.
    4) AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION - the output location.
"""


# [START sample_submit_job]
def sample_submit_job() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.documents import AnalyzeDocumentsClient

    endpoint = os.environ["AZURE_LANGUAGE_DOCUMENTS_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    source_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION"]
    target_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION"]

    client = AnalyzeDocumentsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    with client:
        poller = client.begin_submit_job(
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


# [END sample_submit_job]


if __name__ == "__main__":
    sample_submit_job()
