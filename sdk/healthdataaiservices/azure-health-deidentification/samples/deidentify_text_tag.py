# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: deidentify_text_tag.py

DESCRIPTION:
    This sample demonstrates the most simple de-identification scenario, calling the service to identify (tag) PHI entities.

USAGE:
    python deidentify_text_tag.py

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


def deidentify_text_tag():
    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    # [START tag]
    body = DeidentificationContent(
        input_text="Hello, I'm Dr. John Smith.", operation_type=DeidentificationOperationType.TAG
    )
    result: DeidentificationResult = client.deidentify_text(body)
    print(f'\nOriginal Text:    "{body.input_text}"')

    if result.tagger_result and result.tagger_result.entities:
        print(f"Tagged Entities:")
        for entity in result.tagger_result.entities:
            print(
                f'\tEntity Text: "{entity.text}", Entity Category: "{entity.category}", Offset: "{entity.offset.code_point}", Length: "{entity.length.code_point}"'
            )
    else:
        print("\tNo tagged entities found.")
    # [END tag]


if __name__ == "__main__":
    deidentify_text_tag()
