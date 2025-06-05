# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: deidentify_text_redact_async.py

DESCRIPTION:
    This sample demonstrates the most simple de-identification scenario, calling the service to redact
    PHI values in a string.

USAGE:
    python deidentify_text_redact_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the service URL endpoint for a de-identification service.
"""


import asyncio
from azure.health.deidentification.aio import DeidentificationClient
from azure.health.deidentification.models import (
    DeidentificationContent,
    DeidentificationOperationType,
    DeidentificationResult,
)
from azure.identity.aio import DefaultAzureCredential
import os


async def deidentify_text_redact_async():
    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    async with client:
        body = DeidentificationContent(
            input_text="It's great to work at Contoso.", operation_type=DeidentificationOperationType.REDACT
        )
        result: DeidentificationResult = await client.deidentify_text(body)
        print(f'\nOriginal Text:    "{body.input_text}"')
        print(f'Redacted Text:    "{result.output_text}"')  # Redacted output: "It's great to work at [organization]."

        await credential.close()


async def main():
    await deidentify_text_redact_async()


if __name__ == "__main__":
    asyncio.run(main())
