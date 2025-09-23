# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: deidentify_text_surrogate.py

DESCRIPTION:
    This sample demonstrates the most simple de-identification scenario, calling the service to replace
    PHI in a string with surrogate values.

USAGE:
    python deidentify_text_surrogate.py

    Set the environment variables with your own values before running the sample:
    1) HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT - the service URL endpoint for a de-identification service.
"""


def deidentify_text_surrogate():
    # [START surrogate]
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationContent,
        DeidentificationOperationType,
        DeidentificationResult,
    )
    from azure.identity import DefaultAzureCredential
    import os

    endpoint = os.environ["HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    body = DeidentificationContent(
        input_text="Hello, my name is John Smith.", operation_type=DeidentificationOperationType.SURROGATE
    )
    result: DeidentificationResult = client.deidentify_text(body)
    print(f'\nOriginal Text:     "{body.input_text}"')
    print(f'Surrogated Text:   "{result.output_text}"')  # Surrogated output: Hello, my name is <synthetic name>.
    # [END surrogate]


if __name__ == "__main__":
    deidentify_text_surrogate()
