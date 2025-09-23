# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: deidentify_text_surrogate_only.py

DESCRIPTION:
    This sample demonstrates de-identification using the SurrogateOnly operation, which returns output text
    where user-defined PHI entities are replaced with realistic replacement values.

USAGE:
    python deidentify_text_surrogate_only.py

    Set the environment variables with your own values before running the sample:
    1) HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT - the service URL endpoint for a de-identification service.
"""


def deidentify_text_surrogate_only():
    # [START surrogate_only]
    from azure.health.deidentification import DeidentificationClient
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
    from azure.identity import DefaultAzureCredential
    import os

    endpoint = os.environ["HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    # Define the entities to be surrogated - targeting "John Smith" at position 18-28
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

    result: DeidentificationResult = client.deidentify_text(body)
    print(f'\nOriginal Text:        "{body.input_text}"')
    print(f'Surrogate Only Text:  "{result.output_text}"')  # Surrogated output: Hello, my name is <synthetic name>.
    # [END surrogate_only]


if __name__ == "__main__":
    deidentify_text_surrogate_only()
