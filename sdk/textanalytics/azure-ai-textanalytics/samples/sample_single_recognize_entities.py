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
"""

import os


class SingleRecognizeEntitiesSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def recognize_entities(self):
        # [START single_recognize_entities]
        from azure.ai.textanalytics import single_recognize_entities, TextAnalyticsApiKeyCredential

        text = "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975," \
               " to develop and sell BASIC interpreters for the Altair 8800."

        result = single_recognize_entities(
            endpoint=self.endpoint,
            credential=TextAnalyticsApiKeyCredential(self.key),
            input_text=text,
            language="en"
        )

        for entity in result.entities:
            print("Entity: {}".format(entity.text))
            print("Category: {}".format(entity.category))
            print("Confidence Score: {0:.3f}\n".format(entity.score))
        # [END single_recognize_entities]


if __name__ == '__main__':
    sample = SingleRecognizeEntitiesSample()
    sample.recognize_entities()

