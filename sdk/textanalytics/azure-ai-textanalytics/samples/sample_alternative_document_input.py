# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_alternative_document_input.py

DESCRIPTION:
    This sample shows an alternative way to pass in the input documents.
    Here we specify our own IDs and the text language along with the text.

USAGE:
    python sample_alternative_document_input.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os
import logging

_LOGGER = logging.getLogger(__name__)

class AlternativeDocumentInputSample(object):
    endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

    def alternative_document_input(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))

        documents = [
            {"id": "0", "language": "en", "text": "I had the best day of my life."},
            {"id": "1", "language": "en",
             "text": "This was a waste of my time. The speaker put me to sleep."},
            {"id": "2", "language": "es", "text": "No tengo dinero ni nada que dar..."},
            {"id": "3", "language": "fr",
             "text": "L'hôtel n'était pas très confortable. L'éclairage était trop sombre."}
        ]

        result = text_analytics_client.analyze_sentiment(documents)

        for idx, doc in enumerate(result):
            if not doc.is_error:
                print("Document text: {}".format(documents[idx]))
                print("Language detected: {}".format(doc.primary_language.name))
                print("ISO6391 name: {}".format(doc.primary_language.iso6391_name))
                print("Confidence score: {}\n".format(doc.primary_language.confidence_score))
            if doc.is_error:
                print(doc.id, doc.error)


if __name__ == '__main__':
    sample = AlternativeDocumentInputSample()
    sample.alternative_document_input()
