# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: deidentify_text_redact.py

DESCRIPTION:
    This sample demonstrates the most simple de-identification scenario, calling the service to redact
    PHI values in a string.

USAGE:
    python deidentify_text_redact.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the service URL endpoint for a de-identification service.
"""


from azure.health.deidentification import DeidentificationClient
from azure.health.deidentification.models import (
    DeidentificationContent,
    DeidentificationOperationType,
    DeidentificationResult,
)
from azure.identity import DefaultAzureCredential
import os


def deidentify_text_redact():
    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    # [START redact]
    body = DeidentificationContent(
        input_text="It's great to work at Contoso.", operation_type=DeidentificationOperationType.REDACT
    )
    result: DeidentificationResult = client.deidentify_text(body)
    print(f'\nOriginal Text:        "{body.input_text}"')
    print(f'Redacted Text:   "{result.output_text}"')  # Redacted output: "It's great to work at [organization]."
    # [END redact]


if __name__ == "__main__":
    deidentify_text_redact()
