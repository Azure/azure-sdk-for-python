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
"""

import os
import asyncio


class AnalyzeSentimentSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def analyze_sentiment_async(self):
        # [START batch_analyze_sentiment_async]
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))
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
        # [END batch_analyze_sentiment_async]
            print("Overall scores: positive={0:.3f}; neutral={1:.3f}; negative={2:.3f} \n".format(
                doc.sentiment_scores.positive,
                doc.sentiment_scores.neutral,
                doc.sentiment_scores.negative,
            ))
            for idx, sentence in enumerate(doc.sentences):
                print("Sentence {} sentiment: {}".format(idx+1, sentence.sentiment))
                print("Sentence score: positive={0:.3f}; neutral={1:.3f}; negative={2:.3f}".format(
                    sentence.sentiment_scores.positive,
                    sentence.sentiment_scores.neutral,
                    sentence.sentiment_scores.negative,
                ))
                print("Offset: {}".format(sentence.offset))
                print("Length: {}\n".format(sentence.length))
            print("------------------------------------")

    async def alternative_scenario_analyze_sentiment_async(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[TextDocumentInput] and supplying your own IDs and language hints along
        with the text.
        """
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential
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
    await sample.alternative_scenario_analyze_sentiment_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
