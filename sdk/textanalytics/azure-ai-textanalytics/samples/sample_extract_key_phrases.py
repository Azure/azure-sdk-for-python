# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_extract_key_phrases.py

DESCRIPTION:
    This sample demonstrates how to extract key talking points from a batch of documents.

USAGE:
    python sample_extract_key_phrases.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os


class ExtractKeyPhrasesSample(object):

    endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

    def extract_key_phrases(self):
        # [START batch_extract_key_phrases]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        documents = [
            "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
            "I need to take my cat to the veterinarian.",
            "I will travel to South America in the summer.",
        ]

        result = text_analytics_client.extract_key_phrases(documents)
        for doc in result:
            if not doc.is_error:
                print(doc.key_phrases)
            if doc.is_error:
                print(doc.id, doc.error)
        # [END batch_extract_key_phrases]


if __name__ == '__main__':
    sample = ExtractKeyPhrasesSample()
    sample.extract_key_phrases()
