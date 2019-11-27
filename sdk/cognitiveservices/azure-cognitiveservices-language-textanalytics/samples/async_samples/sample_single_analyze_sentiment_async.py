# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_analyze_sentiment_async.py

DESCRIPTION:
    This sample demonstrates how to analyze sentiment from a single string.
    An overall sentiment and a per-sentence sentiment is returned.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_analyze_sentiment_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Overall sentiment: mixed
    Overall scores: positive=0.5048184394836426; neutral=0.1525073200464249; negative=0.342674195766449

    Sentence 1 sentiment: neutral
    Offset: 0
    Length: 35
    Sentence score: positive=0.0220915991812944; neutral=0.9590522050857544; negative=0.0188561752438545

    Sentence 2 sentiment: positive
    Offset: 36
    Length: 32
    Sentence score: positive=0.9965522289276123; neutral=0.0012628735275939; negative=0.0021848580799997

    Sentence 3 sentiment: negative
    Offset: 69
    Length: 39
    Sentence score: positive=0.0130846798419952; neutral=0.3037517666816711; negative=0.6831635236740112
"""

import os
import asyncio


class SingleAnalyzeSentimentSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def analyze_sentiment_async(self):
        from azure.cognitiveservices.language.textanalytics.aio import single_analyze_sentiment

        text = "I visited the restaurant last week. The portions were very generous. However, I did not like what " \
               "I ordered."

        result = await single_analyze_sentiment(
            endpoint=self.endpoint,
            credential=self.key,
            text=text,
            language="en"
        )

        print("Overall sentiment: {}".format(result.sentiment))
        print("Overall scores: positive={}; neutral={}; negative={} \n".format(
            result.document_scores['positive'],
            result.document_scores['neutral'],
            result.document_scores['negative'],
        ))

        for idx, sentence in enumerate(result.sentences):
            print("Sentence {} sentiment: {}".format(idx+1, sentence.sentiment))
            print("Offset: {}".format(sentence.offset))
            print("Length: {}".format(sentence.length))
            print("Sentence score: positive={}; neutral={}; negative={} \n".format(
                sentence.sentence_scores['positive'],
                sentence.sentence_scores['neutral'],
                sentence.sentence_scores['negative'],
            ))


async def main():
    sample = SingleAnalyzeSentimentSampleAsync()
    await sample.analyze_sentiment_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
