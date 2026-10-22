# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: deidentify_text_surrogate_only_async.py

DESCRIPTION:
    This sample demonstrates de-identification using the SurrogateOnly operation, which returns output text
    where user-defined PHI entities are replaced with realistic replacement values.

USAGE:
    python deidentify_text_surrogate_only_async.py

    Set the environment variables with your own values before running the sample:
    1) HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT - the service URL endpoint for a de-identification service.
"""


import asyncio
from azure.health.deidentification.aio import DeidentificationClient
from azure.health.deidentification.models import (
    DeidentificationContent,
    DeidentificationCustomizationOptions,
    DeidentificationOperationType,
    DeidentificationResult,
    PhiCategory,
    SimplePhiEntity,
    TaggedPhiEntities,
    TextEncodingType,
)
from azure.identity.aio import DefaultAzureCredential
import os


async def deidentify_text_surrogate_only_async():
    # [START surrogate_only_async]
    endpoint = os.environ["HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    async with client:
        # Define the entities to be surrogated
        tagged_entities = TaggedPhiEntities(
            encoding=TextEncodingType.CODE_POINT,
            entities=[SimplePhiEntity(category=PhiCategory.PATIENT, offset=18, length=10)],
        )

        # Use SurrogateOnly operation with input locale specification
        body = DeidentificationContent(
            input_text="Hello, my name is John Smith.",
            operation_type=DeidentificationOperationType.SURROGATE_ONLY,
            tagged_entities=tagged_entities,
            customizations=DeidentificationCustomizationOptions(
                input_locale="en-US"  # Specify input text locale for better PHI detection
            ),
        )

        result: DeidentificationResult = await client.deidentify_text(body)
        print(f'\nOriginal Text:        "{body.input_text}"')
        print(f'Surrogate Only Text:  "{result.output_text}"')  # Only "John Smith" is replaced

        await credential.close()
    # [END surrogate_only_async]


async def main():
    await deidentify_text_surrogate_only_async()


if __name__ == "__main__":
    asyncio.run(main())
