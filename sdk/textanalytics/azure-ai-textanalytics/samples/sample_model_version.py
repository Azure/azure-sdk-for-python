# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_model_version.py

DESCRIPTION:
    This sample demonstrates how to set the model_version for pre-built Text Analytics models.
    Recognize entities is used in this sample, but the concept applies generally to all pre-built Text Analytics models.

    By default, model_version is set to "latest". This indicates that the latest generally available version
    of the model will be used. Model versions are date based, e.g "2021-06-01".
    See the documentation for a list of all model versions:
    https://aka.ms/text-analytics-model-versioning

USAGE:
    python sample_model_version.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""

import os


def sample_model_version() -> None:
    print("--------------Choosing model_version sample--------------")
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient, RecognizeEntitiesAction

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    documents = [
        "I work for Foo Company, and we hired Contoso for our annual founding ceremony. The food \
        was amazing and we all can't say enough good words about the quality and the level of service."
    ]

    print("\nSetting model_version='latest' with recognize_entities")
    result = text_analytics_client.recognize_entities(documents, model_version="latest")
    result = [review for review in result if not review.is_error]

    print("...Results of Recognize Entities:")
    for review in result:
        for entity in review.entities:
            print(f"......Entity '{entity.text}' has category '{entity.category}'")

    print("\nSetting model_version='latest' with recognize entities action in begin_analyze_actions")
    poller = text_analytics_client.begin_analyze_actions(
        documents,
        actions=[
            RecognizeEntitiesAction(model_version="latest")
        ]
    )

    print("...Results of Recognize Entities Action:")
    document_results = poller.result()
    for action_results in document_results:
        action_result = action_results[0]
        if action_result.kind == "EntityRecognition":
            for entity in action_result.entities:
                print(f"......Entity '{entity.text}' has category '{entity.category}'")
        elif action_result.kind == "DocumentError":
            print("......Is an error with code '{}' and message '{}'".format(
                action_result.code, action_result.message
            ))


if __name__ == '__main__':
    sample_model_version()
