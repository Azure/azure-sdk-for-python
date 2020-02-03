# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_recognize_pii_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize personally identifiable
    information in a single string. For the list of supported entity types,
    see https://aka.ms/tanerpii

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_recognize_pii_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key
"""

import os


class SingleRecognizePiiEntitiesSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def recognize_pii_entities(self):
        # [START single_recognize_pii_entities]
        from azure.ai.textanalytics import single_recognize_pii_entities, TextAnalyticsApiKeyCredential

        text = "The employee's ABA number is 111000025 and his SSN is 555-55-5555."

        result = single_recognize_pii_entities(
            endpoint=self.endpoint,
            credential=TextAnalyticsApiKeyCredential(self.key),
            input_text=text,
            language="en"
        )

        for entity in result.entities:
            print("Entity: {}".format(entity.text))
            print("Category: {}".format(entity.category))
            print("Confidence Score: {}\n".format(entity.score))
        # [END single_recognize_pii_entities]


if __name__ == '__main__':
    sample = SingleRecognizePiiEntitiesSample()
    sample.recognize_pii_entities()
