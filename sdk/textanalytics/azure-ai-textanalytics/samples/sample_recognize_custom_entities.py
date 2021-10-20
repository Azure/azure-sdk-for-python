# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_custom_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize custom entities in documents.
    Recognizing custom entities is available as an action type through the begin_analyze_actions API.

    To train a model to recognize your custom entities, see https://aka.ms/azsdk/textanalytics/customentityrecognition

USAGE:
    python sample_recognize_custom_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
    3) AZURE_TEXT_ANALYTICS_PROJECT_NAME - your Text Analytics Language Studio project name
    4) AZURE_TEXT_ANALYTICS_DEPLOYMENT_NAME - your Text Analytics deployed model name
"""


import os


def sample_recognize_custom_entities():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import (
        TextAnalyticsClient,
        RecognizeCustomEntitiesAction
    )

    endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]
    project_name = os.environ["AZURE_TEXT_ANALYTICS_PROJECT_NAME"]
    deployed_model_name = os.environ["AZURE_TEXT_ANALYTICS_DEPLOYMENT_NAME"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    document = [
        "The Grantor(s), John Smith, who also appears of record as John A. Smith, for and in consideration of "
        "Ten dollars and Zero cents ($10.00) and other good and valuable consideration in hand paid, conveys, and "
        "warrants to Jane Doe, the following described real estate, situated in the County of King, State of "
        "Washington: Lot A, King County Short Plat Number AAAAAAAA, recorded under Recording Number AAAAAAAAA in "
        "King County, Washington."
    ]

    poller = text_analytics_client.begin_analyze_actions(
        document,
        actions=[
            RecognizeCustomEntitiesAction(
                project_name=project_name,
                deployment_name=deployed_model_name
            ),
        ],
    )

    document_results = poller.result()
    for result in document_results:
        custom_entities_result = result[0]  # first document, first result
        if not custom_entities_result.is_error:
            for entity in custom_entities_result.entities:
                if entity.category == "Seller Name":
                    print("The seller of the property is {} with confidence score {}.".format(
                        entity.text, entity.confidence_score)
                    )
                if entity.category == "Buyer Name":
                    print("The buyer of the property is {} with confidence score {}.".format(
                        entity.text, entity.confidence_score)
                    )
                if entity.category == "Buyer Fee":
                    print("The buyer fee is {} with confidence score {}.".format(
                        entity.text, entity.confidence_score)
                    )
                if entity.category == "Lot Number":
                    print("The lot number of the property is {} with confidence score {}.".format(
                        entity.text, entity.confidence_score)
                    )
                if entity.category == "Short Plat Number":
                    print("The short plat number of the property is {} with confidence score {}.".format(
                        entity.text, entity.confidence_score)
                    )
                if entity.category == "Recording Number":
                    print("The recording number of the property is {} with confidence score {}.".format(
                        entity.text, entity.confidence_score)
                    )
        else:
            print("...Is an error with code '{}' and message '{}'".format(
                custom_entities_result.code, custom_entities_result.message
            ))


if __name__ == "__main__":
    sample_recognize_custom_entities()
