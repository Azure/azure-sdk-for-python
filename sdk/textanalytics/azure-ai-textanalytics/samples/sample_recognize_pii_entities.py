# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_pii_entities.py

DESCRIPTION:
    This sample demonstrates how to recognize personally identifiable information in a batch of documents.
    The endpoint recognize_pii_entities is only available for API version v3.1-preview and up.

USAGE:
    python sample_recognize_pii_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os


class RecognizePiiEntitiesSample(object):

    def recognize_pii_entities(self):
        # [START recognize_pii_entities]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        documents = [
            "The employee's SSN is 859-98-0987.",
            "Is 998.214.865-68 your Brazilian CPF number?",
            "My phone number is 555-555-5555"
        ]

        result = text_analytics_client.recognize_pii_entities(documents)
        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}".format(documents[idx]))
            print("Redacted document text: {}".format(doc.redacted_text))
            for entity in doc.entities:
                print("...Entity: {}".format(entity.text))
                print("......Category: {}".format(entity.category))
                print("......Confidence Score: {}\n".format(entity.confidence_score))
        # [END recognize_pii_entities]


if __name__ == '__main__':
    sample = RecognizePiiEntitiesSample()
    sample.recognize_pii_entities()
