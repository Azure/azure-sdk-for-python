# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_recognize_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize entities in a single string.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_recognize_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Entity: Microsoft
    Type: Organization
    Confidence Score: 1.000

    Entity: Bill Gates
    Type: Person
    Confidence Score: 1.000

    Entity: Paul Allen
    Type: Person
    Confidence Score: 0.999

    Entity: April 4, 1975
    Type: DateTime
    Confidence Score: 0.800

    Entity: Altair
    Type: Organization
    Confidence Score: 0.525

    Entity: 8800
    Type: Quantity
    Confidence Score: 0.80
"""

import os


class SingleRecognizeEntitiesSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def recognize_entities(self):
        # [START single_recognize_entities]
        from azure.ai.textanalytics import single_recognize_entities, TextAnalyticsSubscriptionKeyCredential

        text = "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975," \
               " to develop and sell BASIC interpreters for the Altair 8800."

        result = single_recognize_entities(
            endpoint=self.endpoint,
            credential=TextAnalyticsSubscriptionKeyCredential(self.key),
            input_text=text,
            language="en"
        )

        for entity in result.entities:
            print("Entity: {}".format(entity.text))
            print("Type: {}".format(entity.type))
            print("Confidence Score: {0:.3f}\n".format(entity.score))
        # [END single_recognize_entities]


if __name__ == '__main__':
    sample = SingleRecognizeEntitiesSample()
    sample.recognize_entities()

