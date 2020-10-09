# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_sentiment.py

DESCRIPTION:
    This sample demonstrates how to analyze sentiment in documents.
    An overall and per-sentence sentiment is returned.

USAGE:
    python sample_analyze_sentiment.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os


class AnalyzeSentimentSample(object):

    def analyze_sentiment(self):
        # [START analyze_sentiment]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        documents = [
            "I had the best day of my life.",
            "This was a waste of my time. The speaker put me to sleep.",
            "No tengo dinero ni nada que dar...",
            "L'hôtel n'était pas très confortable. L'éclairage était trop sombre."
        ]

        result = text_analytics_client.analyze_sentiment(documents)
        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}".format(documents[idx]))
            print("Overall sentiment: {}".format(doc.sentiment))
        # [END analyze_sentiment]
            print("Overall confidence scores: positive={}; neutral={}; negative={} \n".format(
                doc.confidence_scores.positive,
                doc.confidence_scores.neutral,
                doc.confidence_scores.negative,
            ))
            for sentence in doc.sentences:
                print("Sentence '{}' has sentiment: {}".format(sentence.text, sentence.sentiment))
                print("...Sentence is {} characters from the start of the document and is {} characters long".format(
                    sentence.offset, len(sentence.text)
                ))
                print("...Sentence confidence scores: positive={}; neutral={}; negative={}".format(
                    sentence.confidence_scores.positive,
                    sentence.confidence_scores.neutral,
                    sentence.confidence_scores.negative,
                ))
            print("------------------------------------")


if __name__ == '__main__':
    sample = AnalyzeSentimentSample()
    sample.analyze_sentiment()
