# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_dynamically_classify.py

DESCRIPTION:
    This sample demonstrates how to dynamically classify documents into one or multiple categories.
    No model training is required to use dynamic classification.

USAGE:
    python sample_dynamically_classify.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""


import os


def sample_dynamically_classify() -> None:
    # [START dynamic_classification]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )
    documents = [
        "The WHO is issuing a warning about Monkey Pox.",
        "Mo Salah plays in Liverpool FC in England.",
    ]
    result = text_analytics_client.dynamically_classify(
        documents,
        categories=["Health", "Politics", "Music", "Sports"],
        classification_type="Multi"
    )

    for doc, classification_result in zip(documents, result):
        if classification_result.kind == "DynamicClassification":
            classifications = classification_result.classifications
            print(f"\n'{doc}' classifications:\n")
            for classification in classifications:
                print("Category '{}' with confidence score {}.".format(
                    classification.category, classification.confidence_score
                ))
        elif classification_result.is_error is True:
            print("Document '{}' has an error with code '{}' and message '{}'".format(
                doc, classification_result.code, classification_result.message
            ))
    # [END dynamic_classification]


if __name__ == "__main__":
    sample_dynamically_classify()
