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
"""

import os


class SingleAnalyzeSentimentSample(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    def analyze_sentiment(self):
        # [START single_analyze_sentiment]
        from azure.ai.textanalytics import single_analyze_sentiment, TextAnalyticsApiKeyCredential

        text = "I visited the restaurant last week. The portions were very generous. However, I did not like what " \
               "I ordered."

        result = single_analyze_sentiment(
            endpoint=self.endpoint,
            credential=TextAnalyticsApiKeyCredential(self.key),
            input_text=text,
            language="en"
        )

        print("Overall sentiment: {}".format(result.sentiment))
        print("Overall scores: positive={0:.3f}; neutral={1:.3f}; negative={2:.3f} \n".format(
            result.sentiment_scores.positive,
            result.sentiment_scores.neutral,
            result.sentiment_scores.negative,
        ))

        for idx, sentence in enumerate(result.sentences):
            print("Sentence {} sentiment: {}".format(idx+1, sentence.sentiment))
            print("Offset: {}".format(sentence.offset))
            print("Length: {}".format(sentence.length))
            print("Sentence score: positive={0:.3f}; neutral={1:.3f}; negative={2:.3f} \n".format(
                sentence.sentiment_scores.positive,
                sentence.sentiment_scores.neutral,
                sentence.sentiment_scores.negative,
            ))
        # [END single_analyze_sentiment]


if __name__ == '__main__':
    sample = SingleAnalyzeSentimentSample()
    sample.analyze_sentiment()
