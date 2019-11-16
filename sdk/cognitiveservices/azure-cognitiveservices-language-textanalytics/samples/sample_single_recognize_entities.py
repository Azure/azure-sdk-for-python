# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_recognize_entities.py

DESCRIPTION:
    This samples demonstrates how to recognize entities in a single string.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_recognize_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_COGNITIVE_SERVICES_KEY - your cognitive services account key

OUTPUT:
    Entity: Microsoft
    Type: Organization
    Confidence Score: 1.0

    Entity: Bill Gates
    Type: Person
    Confidence Score: 0.999847412109375

    Entity: Paul Allen
    Type: Person
    Confidence Score: 0.9988409876823425

    Entity: April 4, 1975
    Type: DateTime
    Confidence Score: 0.8

    Entity: Altair
    Type: Organization
    Confidence Score: 0.5250527262687683

    Entity: 8800
    Type: Quantity
    Confidence Score: 0.8
"""

import os


class SingleRecognizeEntitiesSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_COGNITIVE_SERVICES_KEY")

    def recognize_entities(self):
        from azure.cognitiveservices.language.textanalytics import single_recognize_entities

        text = "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975," \
               " to develop and sell BASIC interpreters for the Altair 8800."

        result = single_recognize_entities(
            endpoint=self.endpoint,
            credential=self.key,
            text=text,
            language="en"
        )

        for entity in result:
            print("Entity: {}".format(entity.text))
            print("Type: {}".format(entity.type))
            print("Confidence Score: {}\n".format(entity.score))


if __name__ == '__main__':
    sample = SingleRecognizeEntitiesSample()
    sample.recognize_entities()

