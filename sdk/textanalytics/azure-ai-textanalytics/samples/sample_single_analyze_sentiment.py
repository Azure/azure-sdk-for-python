# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_analyze_sentiment.py

DESCRIPTION:
    This sample demonstrates how to analyze sentiment from a single string.
    An overall sentiment and a per-sentence sentiment is returned.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_analyze_sentiment.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Overall sentiment: mixed
    Overall scores: positive=0.338; neutral=0.432; negative=0.230

    Sentence 1 sentiment: neutral
    Offset: 0
    Length: 35
    Sentence score: positive=0.006; neutral=0.987; negative=0.007

    Sentence 2 sentiment: positive
    Offset: 36
    Length: 32
    Sentence score: positive=0.999; neutral=0.000; negative=0.001

    Sentence 3 sentiment: negative
    Offset: 69
    Length: 39
    Sentence score: positive=0.010; neutral=0.307; negative=0.683

"""

import os


class SingleAnalyzeSentimentSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def analyze_sentiment(self):
        # [START single_analyze_sentiment]
        from azure.ai.textanalytics import single_analyze_sentiment, TextAnalyticsAPIKeyCredential

        text = "I visited the restaurant last week. The portions were very generous. However, I did not like what " \
               "I ordered."

        result = single_analyze_sentiment(
            endpoint=self.endpoint,
            credential=TextAnalyticsAPIKeyCredential(self.key),
            input_text=text,
            language="en"
        )

        print("Overall sentiment: {}".format(result.sentiment))
        print("Overall scores: positive={0:.3f}; neutral={1:.3f}; negative={2:.3f} \n".format(
            result.document_scores.positive,
            result.document_scores.neutral,
            result.document_scores.negative,
        ))

        for idx, sentence in enumerate(result.sentences):
            print("Sentence {} sentiment: {}".format(idx+1, sentence.sentiment))
            print("Offset: {}".format(sentence.offset))
            print("Length: {}".format(sentence.length))
            print("Sentence score: positive={0:.3f}; neutral={1:.3f}; negative={2:.3f} \n".format(
                sentence.sentence_scores.positive,
                sentence.sentence_scores.neutral,
                sentence.sentence_scores.negative,
            ))
        # [END single_analyze_sentiment]


if __name__ == '__main__':
    sample = SingleAnalyzeSentimentSample()
    sample.analyze_sentiment()
