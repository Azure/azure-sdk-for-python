# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_realtime_deidentification.py

DESCRIPTION:
    This sample demonstrates the most simple deidentification scenario. It takes in a string of text and will return
    the deidentified text.

USAGE:
    python sample_realtime_deidentification.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the endpoint to your Deidentification Service resource.
"""


def sample_realtime_deidentification():
    # [START realtime_deidentification]
    import os
    from azure.identity import DefaultAzureCredential
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationResult,
        DeidentificationContent,
        OperationType,
        DocumentDataType,
    )

    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    endpoint = endpoint.replace("https://", "")

    credential = DefaultAzureCredential()

    client = DeidentificationClient(endpoint, credential)

    body = DeidentificationContent(input_text="Hello, my name is John Smith.")

    result: DeidentificationResult = client.deidentify(body)
    print(f'Original Text:     "{body.input_text}"')
    print(f'Deidentified Text: "{result.output_text}"')
    # [END realtime_deidentification]


if __name__ == "__main__":
    sample_realtime_deidentification()
