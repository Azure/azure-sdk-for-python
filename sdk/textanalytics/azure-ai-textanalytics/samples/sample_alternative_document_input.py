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
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key
"""

import os


def sample_alternative_document_input() -> None:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

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
        if doc.is_error is False:
            print(f"Document text: {documents[idx]}")
            print(f"Language detected: {doc.primary_language.name}")
            print(f"ISO6391 name: {doc.primary_language.iso6391_name}")
            print(f"Confidence score: {doc.primary_language.confidence_score}\n")
        else:
            print(doc.id, doc.error)


if __name__ == '__main__':
    sample_alternative_document_input()
