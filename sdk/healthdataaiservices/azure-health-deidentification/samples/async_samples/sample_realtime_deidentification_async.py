# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_realtime_deidentification_async.py

DESCRIPTION:
    This sample demonstrates the most simple deidentification scenario. It takes in a string of text and will return
    the deidentified text.

USAGE:
    python sample_realtime_deidentification_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the endpoint to your Deidentification Service resource.
"""
import asyncio


async def sample_realtime_deidentification_async():
    # [START realtime_deidentification_async]
    import os
    from azure.identity.aio import DefaultAzureCredential
    from azure.health.deidentification.aio import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationResult,
        DeidentificationContent,
    )

    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    endpoint = endpoint.replace("https://", "")

    credential = DefaultAzureCredential()

    client = DeidentificationClient(endpoint, credential)

    body = DeidentificationContent(input_text="Hello, my name is John Smith.")

    async with client:
        result: DeidentificationResult = await client.deidentify(body)

    await credential.close()
    print(f'Original Text:     "{body.input_text}"')
    print(f'Deidentified Text: "{result.output_text}"')
    # [END realtime_deidentification]


async def main():
    await sample_realtime_deidentification_async()


if __name__ == "__main__":
    asyncio.run(main())
