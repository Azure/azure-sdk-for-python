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

    def alternative_document_input(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

        documents = [
            {"id": "0", "country_hint": "US", "text": "I had the best day of my life. I decided to go sky-diving and it made me appreciate my whole life so much more. I developed a deep-connection with my instructor as well."},
            {"id": "1", "country_hint": "GB",
             "text": "This was a waste of my time. The speaker put me to sleep."},
            {"id": "2", "country_hint": "MX", "text": "No tengo dinero ni nada que dar..."},
            {"id": "3", "country_hint": "FR",
             "text": "L'hôtel n'était pas très confortable. L'éclairage était trop sombre."}
        ]

        result = text_analytics_client.detect_language(documents)

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
