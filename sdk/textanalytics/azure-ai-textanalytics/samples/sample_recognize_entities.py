# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize named entities in a batch of documents.

USAGE:
    python sample_recognize_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os


class RecognizeEntitiesSample(object):

    endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

    def recognize_entities(self):
        # [START batch_recognize_entities]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        documents = [
            "Microsoft was founded by Bill Gates and Paul Allen.",
            "I had a wonderful trip to Seattle last week.",
            "I visited the Space Needle 2 times.",
        ]

        result = text_analytics_client.recognize_entities(documents)
        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("\nDocument text: {}".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: \t", entity.text, "\tCategory: \t", entity.category,
                      "\tConfidence Score: \t", entity.confidence_score)
        # [END batch_recognize_entities]


if __name__ == '__main__':
    sample = RecognizeEntitiesSample()
    sample.recognize_entities()
