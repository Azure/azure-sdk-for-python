# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_sentiment_async.py

DESCRIPTION:
    This sample demonstrates how to analyze sentiment in a batch of documents.
    An overall and per-sentence sentiment is returned.

USAGE:
    python sample_analyze_sentiment_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Document text: I had the best day of my life.
    Overall sentiment: positive
    Overall scores: positive=0.9992358684539795; neutral=0.0006491420208476; negative=0.0001150449024863

    Sentence 1 sentiment: positive
    Sentence score: positive=0.9992358684539795; neutral=0.0006491420208476; negative=0.0001150449024863
    Offset: 0
    Length: 30

    ------------------------------------
    Document text: This was a waste of my time. The speaker put me to sleep.
    Overall sentiment: negative
    Overall scores: positive=0.0611404217779636; neutral=0.4256836175918579; negative=0.513175904750824

    Sentence 1 sentiment: negative
    Sentence score: positive=1.68700626091e-05; neutral=6.6324328145e-06; negative=0.999976396560669
    Offset: 0
    Length: 28

    Sentence 2 sentiment: neutral
    Sentence score: positive=0.1222639754414558; neutral=0.8513606190681458; negative=0.0263753551989794
    Offset: 29
    Length: 28

    ------------------------------------
    Document text: No tengo dinero ni nada que dar...
    Overall sentiment: negative
    Overall scores: positive=0.0255409516394138; neutral=0.0314255990087986; negative=0.9430333375930786

    Sentence 1 sentiment: negative
    Sentence score: positive=0.0255409516394138; neutral=0.0314255990087986; negative=0.9430333375930786
    Offset: 0
    Length: 34

    ------------------------------------
    Document text: L'hôtel n'était pas très confortable. L'éclairage était trop sombre.
    Overall sentiment: negative
    Overall scores: positive=0.1645563840866089; neutral=0.0295139290392399; negative=0.8059296607971191

    Sentence 1 sentiment: negative
    Sentence score: positive=0.1857066750526428; neutral=0.0316520929336548; negative=0.7826411724090576
    Offset: 0
    Length: 37

    Sentence 2 sentiment: negative
    Sentence score: positive=0.1434061080217361; neutral=0.0273757670074701; negative=0.8292181491851807
    Offset: 38
    Length: 30

    ------------------------------------
"""

import os
import asyncio


class AnalyzeSentimentSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def analyze_sentiment_async(self):
        from azure.cognitiveservices.language.textanalytics.aio import TextAnalyticsClient
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=self.key)
        documents = [
            "I had the best day of my life.",
            "This was a waste of my time. The speaker put me to sleep.",
            "No tengo dinero ni nada que dar...",
            "L'hôtel n'était pas très confortable. L'éclairage était trop sombre."
        ]

        async with text_analytics_client:
            result = await text_analytics_client.analyze_sentiment(documents)

        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}".format(documents[idx]))
            print("Overall sentiment: {}".format(doc.sentiment))
            print("Overall scores: positive={}; neutral={}; negative={} \n".format(
                doc.document_scores['positive'],
                doc.document_scores['neutral'],
                doc.document_scores['negative'],
            ))
            for idx, sentence in enumerate(doc.sentences):
                print("Sentence {} sentiment: {}".format(idx+1, sentence.sentiment))
                print("Sentence score: positive={}; neutral={}; negative={}".format(
                    sentence.sentence_scores['positive'],
                    sentence.sentence_scores['neutral'],
                    sentence.sentence_scores['negative'],
                ))
                print("Offset: {}".format(sentence.offset))
                print("Length: {}\n".format(sentence.length))
            print("------------------------------------")

    async def advanced_scenario_analyze_sentiment_async(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[MultiLanguageInput] and supplying your own IDs and language hints along
        with the text.
        """
        from azure.cognitiveservices.language.textanalytics.aio import TextAnalyticsClient
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=self.key)

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

        async with text_analytics_client:
            result = await text_analytics_client.analyze_sentiment(
                documents,
                show_stats=True,
                model_version="latest",
                response_hook=callback
            )


async def main():
    sample = AnalyzeSentimentSampleAsync()
    await sample.analyze_sentiment_async()
    await sample.advanced_scenario_analyze_sentiment_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
