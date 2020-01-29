# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_sentiment.py

DESCRIPTION:
    This sample demonstrates how to analyze sentiment in a batch of documents.
    An overall and per-sentence sentiment is returned.

USAGE:
    python sample_analyze_sentiment.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Document text: I had the best day of my life.
    Overall sentiment: positive
    Overall scores: positive=0.999; neutral=0.001; negative=0.000

    Sentence 1 sentiment: positive
    Sentence score: positive=0.999; neutral=0.001; negative=0.000
    Offset: 0
    Length: 30

    ------------------------------------
    Document text: This was a waste of my time. The speaker put me to sleep.
    Overall sentiment: negative
    Overall scores: positive=0.061; neutral=0.426; negative=0.513

    Sentence 1 sentiment: negative
    Sentence score: positive=0.000; neutral=0.000; negative=1.000
    Offset: 0
    Length: 28

    Sentence 2 sentiment: neutral
    Sentence score: positive=0.122; neutral=0.851; negative=0.026
    Offset: 29
    Length: 28

    ------------------------------------
    Document text: No tengo dinero ni nada que dar...
    Overall sentiment: negative
    Overall scores: positive=0.026; neutral=0.031; negative=0.943

    Sentence 1 sentiment: negative
    Sentence score: positive=0.026; neutral=0.031; negative=0.943
    Offset: 0
    Length: 34

    ------------------------------------
    Document text: L'hôtel n'était pas très confortable. L'éclairage était trop sombre.
    Overall sentiment: negative
    Overall scores: positive=0.165; neutral=0.030; negative=0.806

    Sentence 1 sentiment: negative
    Sentence score: positive=0.186; neutral=0.032; negative=0.783
    Offset: 0
    Length: 37

    Sentence 2 sentiment: negative
    Sentence score: positive=0.143; neutral=0.027; negative=0.829
    Offset: 38
    Length: 30

    ------------------------------------

"""

import os


class AnalyzeSentimentSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def analyze_sentiment(self):
        # [START batch_analyze_sentiment]
        from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))
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
        # [END batch_analyze_sentiment]
            print("Overall scores: positive={0:.3f}; neutral={1:.3f}; negative={2:.3f} \n".format(
                doc.document_scores.positive,
                doc.document_scores.neutral,
                doc.document_scores.negative,
            ))
            for idx, sentence in enumerate(doc.sentences):
                print("Sentence {} sentiment: {}".format(idx+1, sentence.sentiment))
                print("Sentence score: positive={0:.3f}; neutral={1:.3f}; negative={2:.3f}".format(
                    sentence.sentence_scores.positive,
                    sentence.sentence_scores.neutral,
                    sentence.sentence_scores.negative,
                ))
                print("Offset: {}".format(sentence.offset))
                print("Length: {}\n".format(sentence.length))
            print("------------------------------------")

    def alternative_scenario_analyze_sentiment(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[TextDocumentInput] and supplying your own IDs and language hints along
        with the text.
        """
        from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))

        documents = [
            {"id": "0", "language": "en", "text": "I had the best day of my life."},
            {"id": "1", "language": "en",
             "text": "This was a waste of my time. The speaker put me to sleep."},
            {"id": "2", "language": "es", "text": "No tengo dinero ni nada que dar..."},
            {"id": "3", "language": "fr",
             "text": "L'hôtel n'était pas très confortable. L'éclairage était trop sombre."}
        ]

        extras = []

        def callback(resp):
            extras.append(resp.statistics)
            extras.append(resp.model_version)
            extras.append(resp.raw_response)

        result = text_analytics_client.analyze_sentiment(
            documents,
            show_stats=True,
            model_version="latest",
            response_hook=callback
        )


if __name__ == '__main__':
    sample = AnalyzeSentimentSample()
    sample.analyze_sentiment()
    sample.alternative_scenario_analyze_sentiment()
