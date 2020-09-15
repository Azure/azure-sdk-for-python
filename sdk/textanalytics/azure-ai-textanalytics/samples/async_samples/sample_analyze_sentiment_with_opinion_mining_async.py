# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_sentiment_with_opinion_mining_async.py

DESCRIPTION:
    This sample demonstrates how to analyze sentiment on a more granular level, mining individual
    opinions from reviews (also known as aspect-based sentiment analysis).
    This feature is only available for clients with api version v3.1-preview and up.

    In this sample, we will be a customer who is trying to figure out whether they should stay
    at a specific hotel. We will be looking at which aspects of the hotel are good, and which are
    not.

USAGE:
    python sample_analyze_sentiment_with_opinion_mining_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key

OUTPUT:
    In this sample we will be combing through the reviews of a potential hotel to stay at: Hotel Foo.
    I first found a handful of reviews for Hotel Foo. Let's see if I want to stay here.


    Let's see how many positive and negative reviews of this hotel I have right now
    ...We have 3 positive reviews and 2 negative reviews.

    Looks more positive than negative, but still pretty mixed, so I'm going to drill deeper into the opinions of individual aspects of this hotel

    In order to do that, I'm going to sort them based on whether these opinions are positive, mixed, or negative


    Let's look at the 7 positive opinions users have expressed for aspects of this hotel
    ...Reviewers have the following opinions for the overall positive 'concierge' aspect of the hotel
    ......'positive' opinion 'nice'
    ...Reviewers have the following opinions for the overall positive 'AC' aspect of the hotel
    ......'positive' opinion 'good'
    ......'positive' opinion 'quiet'
    ...Reviewers have the following opinions for the overall positive 'breakfast' aspect of the hotel
    ......'positive' opinion 'good'
    ...Reviewers have the following opinions for the overall positive 'hotel' aspect of the hotel
    ......'positive' opinion 'good'
    ...Reviewers have the following opinions for the overall positive 'breakfast' aspect of the hotel
    ......'positive' opinion 'nice'
    ...Reviewers have the following opinions for the overall positive 'shuttle service' aspect of the hotel
    ......'positive' opinion 'loved'
    ...Reviewers have the following opinions for the overall positive 'view' aspect of the hotel
    ......'positive' opinion 'great'
    ......'positive' opinion 'unobstructed'


    Now let's look at the 1 mixed opinions users have expressed for aspects of this hotel
    ...Reviewers have the following opinions for the overall mixed 'rooms' aspect of the hotel
    ......'positive' opinion 'beautiful'
    ......'negative' opinion 'dirty'


    Finally, let's see the 4 negative opinions users have expressed for aspects of this hotel
    ...Reviewers have the following opinions for the overall negative 'food' aspect of the hotel
    ......'negative' opinion 'unacceptable'
    ...Reviewers have the following opinions for the overall negative 'service' aspect of the hotel
    ......'negative' opinion 'unacceptable'
    ...Reviewers have the following opinions for the overall negative 'elevator' aspect of the hotel
    ......'negative' opinion 'broken'
    ...Reviewers have the following opinions for the overall negative 'toilet' aspect of the hotel
    ......'negative' opinion 'smelly'


    Looking at the breakdown, even though there were more positive opinions of this hotel, I care the most about the food and the toilets in a hotel, so I will be staying elsewhere
"""

import os
import asyncio


class AnalyzeSentimentWithOpinionMiningSampleAsync(object):
    async def analyze_sentiment_with_opinion_mining(self):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
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

        async with text_analytics_client:
            result = await text_analytics_client.analyze_sentiment(documents, show_opinion_mining=True)
        doc_result = [doc for doc in result if not doc.is_error]

        print("\n\nLet's see how many positive and negative reviews of this hotel I have right now")
        positive_reviews = [doc for doc in doc_result if doc.sentiment == "positive"]
        negative_reviews = [doc for doc in doc_result if doc.sentiment == "negative"]
        print("...We have {} positive reviews and {} negative reviews. ".format(len(positive_reviews), len(negative_reviews)))
        print("\nLooks more positive than negative, but still pretty mixed, so I'm going to drill deeper into the opinions of individual aspects of this hotel")

        print("\nIn order to do that, I'm going to sort them based on whether these opinions are positive, mixed, or negative")
        positive_mined_opinions = []
        mixed_mined_opinions = []
        negative_mined_opinions = []

        for document in doc_result:
            for sentence in document.sentences:
                for mined_opinion in sentence.mined_opinions:
                    aspect = mined_opinion.aspect
                    if aspect.sentiment == "positive":
                        positive_mined_opinions.append(mined_opinion)
                    elif aspect.sentiment == "mixed":
                        mixed_mined_opinions.append(mined_opinion)
                    else:
                        negative_mined_opinions.append(mined_opinion)

        print("\n\nLet's look at the {} positive opinions users have expressed for aspects of this hotel".format(len(positive_mined_opinions)))
        for mined_opinion in positive_mined_opinions:
            print("...Reviewers have the following opinions for the overall positive '{}' aspect of the hotel".format(mined_opinion.aspect.text))
            for opinion in mined_opinion.opinions:
                print("......'{}' opinion '{}'".format(opinion.sentiment, opinion.text))

        print("\n\nNow let's look at the {} mixed opinions users have expressed for aspects of this hotel".format(len(mixed_mined_opinions)))
        for mined_opinion in mixed_mined_opinions:
            print("...Reviewers have the following opinions for the overall mixed '{}' aspect of the hotel".format(mined_opinion.aspect.text))
            for opinion in mined_opinion.opinions:
                print("......'{}' opinion '{}'".format(opinion.sentiment, opinion.text))

        print("\n\nFinally, let's see the {} negative opinions users have expressed for aspects of this hotel".format(len(negative_mined_opinions)))
        for mined_opinion in negative_mined_opinions:
            print("...Reviewers have the following opinions for the overall negative '{}' aspect of the hotel".format(mined_opinion.aspect.text))
            for opinion in mined_opinion.opinions:
                print("......'{}' opinion '{}'".format(opinion.sentiment, opinion.text))

        print(
            "\n\nLooking at the breakdown, even though there were more positive opinions of this hotel, "
            "I care the most about the food and the toilets in a hotel, so I will be staying elsewhere"
        )

async def main():
    sample = AnalyzeSentimentWithOpinionMiningSampleAsync()
    await sample.analyze_sentiment_with_opinion_mining()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
