# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_sentiment_with_aspects.py

DESCRIPTION:
    This sample demonstrates how to analyze sentiment on a more granular level, looking into the
    individual aspects of a review (aspect based sentiment analysis).
    This feature is only available for clients with api version v3.1-preview.1.

    In this sample, we will be a customer who is trying to figure out whether they should stay
    at a specific hotel. We will be looking at which aspects of the hotel are good, and which are
    not.

USAGE:
    python sample_analyze_sentiment_with_aspects.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os


class AnalyzeSentimentWithAspectsSample(object):
    def analyze_sentiment_with_aspects(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient, ApiVersion

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            api_version=ApiVersion.V3_1_PREVIEW_1
        )

        print("In this sample we will be combing through the reviews of a potential hotel to stay at: Hotel Foo.")

        print(
            "I first found a handful of reviews for Hotel Foo. Let's see if I want to stay here."
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

        print("\n\nLet's see how many positive and negative reviews of this hotel I have right now")
        positive_reviews = [doc for doc in doc_result if doc.sentiment == "positive"]
        negative_reviews = [doc for doc in doc_result if doc.sentiment == "negative"]
        print("...We have {} positive reviews and {} negative reviews. ".format(len(positive_reviews), len(negative_reviews)))
        print("\nLooks more positive than negative, but still pretty mixed, so I'm going to drill deeper into the individual aspects of each review")

        print("\nIn order to do that, I'm going to sort them based on whether people have positive, mixed, or negative feelings about these aspects")
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
            print("...Reviewers have the following opinions for the overall positive '{}' feature of the hotel".format(aspect.text))
            for opinion in aspect.opinions:
                print("......'{}' opinion '{}'".format(opinion.sentiment, opinion.text))

        print("\n\nNow let's look at the {} aspects with mixed sentiment".format(len(mixed_aspects)))
        for aspect in mixed_aspects:
            print("...Reviewers have the following opinions for the overall mixed '{}' quality of the hotel".format(aspect.text))
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
    sample = AnalyzeSentimentWithAspectsSample()
    sample.analyze_sentiment_with_aspects()
