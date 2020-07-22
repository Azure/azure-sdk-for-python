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

USAGE:
    python sample_recognize_pii_entities.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os


class RecognizePiiEntitiesSample(object):

    def recognize_pii_entities(self):
        # [START batch_recognize_pii_entities]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient, ApiVersion

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, credential=AzureKeyCredential(key), api_version=ApiVersion.V3_1_preview_1
        )
        documents = [
            "The employee's SSN is 555-55-5555.",
            "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check.",
            "Is 998.214.865-68 your Brazilian CPF number?"
        ]

        result = text_analytics_client.recognize_pii_entities(documents)
        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: {}".format(entity.text))
                print("Category: {}".format(entity.category))
                print("Confidence Score: {}\n".format(entity.confidence_score))
        # [END batch_recognize_pii_entities]


if __name__ == '__main__':
    sample = RecognizePiiEntitiesSample()
    sample.recognize_pii_entities()
