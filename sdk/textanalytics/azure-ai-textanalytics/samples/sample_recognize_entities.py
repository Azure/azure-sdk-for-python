# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize named entities in a batch of documents.

    In this sample, we own a catering business. We want to sort the reviews for our business
    based off of which organization hired us.
USAGE:
    python sample_recognize_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""

from __future__ import annotations
import os


def sample_recognize_entities() -> None:
    print(
        "In this sample, we are a catering business, and we're looking to sort the reviews "
        "for our organization based off of the organization that hired us for catering"
    )
    organization_to_reviews: dict[str, list[str]] = {}
    # [START recognize_entities]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    reviews = [
        """I work for Foo Company, and we hired Contoso for our annual founding ceremony. The food
        was amazing and we all can't say enough good words about the quality and the level of service.""",
        """We at the Foo Company re-hired Contoso after all of our past successes with the company.
        Though the food was still great, I feel there has been a quality drop since their last time
        catering for us. Is anyone else running into the same problem?""",
        """Bar Company is over the moon about the service we received from Contoso, the best sliders ever!!!!"""
    ]

    result = text_analytics_client.recognize_entities(reviews)
    result = [review for review in result if not review.is_error]

    for idx, review in enumerate(result):
        for entity in review.entities:
            print(f"Entity '{entity.text}' has category '{entity.category}'")
    # [END recognize_entities]
            if entity.category == 'Organization':
                organization_to_reviews.setdefault(entity.text, [])
                organization_to_reviews[entity.text].append(reviews[idx])

    for organization, reviews in organization_to_reviews.items():
        print(
            "\n\nOrganization '{}' has left us the following review(s): {}".format(
                organization, "\n\n".join(reviews)
            )
        )


if __name__ == '__main__':
    sample_recognize_entities()
