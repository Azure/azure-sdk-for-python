# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_aspect_based_sentiment_analysis.py

DESCRIPTION:
    This sample demonstrates how to conduct aspect based sentiment analysis using the text
    analytics library. This feature is only available for clients with api version v3.1-preview.1.

    In this sample, we will be a customer who is trying to figure out whether they should stay
    at a specific hotel. We will be looking at which aspects of the hotel are good, and which are
    not.

USAGE:
    python sample_aspect_based_sentiment_analysis.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os


class AspectBasedSentimentAnalysisSample(object):
    def aspect_based_sentiment_analysis(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient, ApiVersion

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            api_version=ApiVersion.V3_1_preview_1
        )

        # In this sample we will be combing through the reviews of a potential hotel to stay at: Hotel Foo.
        # We will find what aspects of the hotel are good, and which are bad, and based on this more granular
        # analysis will decide where we will stay

        print(
            "I first found a handful of reviews for Hotel Foo. The hotel was rated 3.5 stars on Contoso.com, "
            "let's see if I want to stay here"
        )

        documents = [
            "The food and service were unacceptable, but the concierge were nice",
            "The rooms were beautiful but dirty. The AC was good and quiet, but the elevator was broken",
            "The breakfast was good, but the toilet was smelly",
            "Loved this hotel - good breakfast - nice shuttle service.",
            "I had a great unobstructed view of the Microsoft campus"
        ]

        result = text_analytics_client.analyze_sentiment(documents, show_aspects=True)
        doc_result = [doc for doc in result if not doc.is_error]

        print("Let's first organize the aspects of the hotel experience into positive, mixed, and negative")
        positive_aspects = []
        mixed_aspects = []
        negative_aspects = []

        for document in doc_result:
            for sentence in document.sentences:
                for aspect in sentence.aspects:
                    if aspect.sentiment == "positive":
                        positive_aspects.append(aspect)
                    elif aspect.sentiment == "mixed":
                        mixed_aspects.append(aspect)
                    else:
                        negative_aspects.append(aspect)

        print("\n\nLet's look at the {} positive aspects of this hotel".format(len(positive_aspects)))
        for aspect in positive_aspects:
            print("...Reviewers have the following opinions for the overall positive '{}' aspect of the hotel".format(aspect.text))
            for opinion in aspect.opinions:
                print("......'{}' opinion '{}'".format(opinion.sentiment, opinion.text))

        print("\n\nNow let's look at the {} aspects with mixed sentiment".format(len(mixed_aspects)))
        for aspect in mixed_aspects:
            print("...Reviewers have the following opinions for the overall mixed '{}' aspect of the hotel".format(aspect.text))
            for opinion in aspect.opinions:
                print("......'{}' opinion '{}'".format(opinion.sentiment, opinion.text))

        print("\n\nFinally, let's see the {} negative aspects of this hotel".format(len(negative_aspects)))
        for aspect in negative_aspects:
            print("...Reviewers have the following opinions for the overall negative '{}' aspect of the hotel".format(aspect.text))
            for opinion in aspect.opinions:
                print("......'{}' opinion '{}'".format(opinion.sentiment, opinion.text))

        print(
            "\n\nLooking at the breakdown, even though there were more positive aspects of this hotel, "
            "I care the most about the food and the toilets in a hotel, so I will be staying elsewhere"
        )


if __name__ == '__main__':
    sample = AspectBasedSentimentAnalysisSample()
    sample.aspect_based_sentiment_analysis()
