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
    This feature is only available for clients with api version v3.1 and up.

    In this sample, we will be a hotel owner looking for complaints users have about our hotel,
    in the hopes that we can improve people's experiences.

USAGE:
    python sample_analyze_sentiment_with_opinion_mining_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_LANGUAGE_ENDPOINT - the endpoint to your Language resource.
    2) AZURE_LANGUAGE_KEY - your Language subscription key

OUTPUT:
    In this sample we will be a hotel owner going through reviews of their hotel to find complaints.
    I first found a handful of reviews for my hotel. Let's see what we have to improve.

    Let's first see the general sentiment of each of these reviews
    ...We have 1 positive reviews, 2 mixed reviews, and 0 negative reviews.

    Since these reviews seem so mixed, and since I'm interested in finding exactly what it is about my hotel that should be improved, let's find the complaints users have about individual aspects of this hotel

    In order to do that, I'm going to extract the targets of a negative sentiment. I'm going to map each of these targets to the mined opinion object we get back to aggregate the reviews by target.

    Let's now go through the aspects of our hotel people have complained about and see what users have specifically said
    Users have made 1 complaints about 'food', specifically saying that it's 'unacceptable'
    Users have made 1 complaints about 'service', specifically saying that it's 'unacceptable'
    Users have made 3 complaints about 'toilet', specifically saying that it's 'smelly', 'broken', 'dirty'


    Looking at the breakdown, I can see what aspects of my hotel need improvement, and based off of both the number and content of the complaints users have made about my toilets, I need to get that fixed ASAP.
"""

import os
import asyncio


async def sample_analyze_sentiment_with_opinion_mining():
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient

    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    print("In this sample we will be a hotel owner going through reviews of their hotel to find complaints.")

    print(
        "I first found a handful of reviews for my hotel. Let's see what we have to improve."
    )

    documents = [
        """
        The food and service were unacceptable, but the concierge were nice.
        After talking to them about the quality of the food and the process to get room service they refunded
        the money we spent at the restaurant and gave us a voucher for near by restaurants.
        """,
        """
        The rooms were beautiful. The AC was good and quiet, which was key for us as outside it was 100F and our baby
        was getting uncomfortable because of the heat. The breakfast was good too with good options and good servicing times.
        The thing we didn't like was that the toilet in our bathroom was smelly. It could have been that the toilet was broken before we arrived.
        Either way it was very uncomfortable. Once we notified the staff, they came and cleaned it and left candles.
        """,
        """
        Nice rooms! I had a great unobstructed view of the Microsoft campus but bathrooms were old and the toilet was dirty when we arrived.
        It was close to bus stops and groceries stores. If you want to be close to campus I will recommend it, otherwise, might be better to stay in a cleaner one
        """
    ]

    async with text_analytics_client:
        result = await text_analytics_client.analyze_sentiment(documents)
    doc_result = [doc for doc in result if not doc.is_error]

    print("\nLet's first see the general sentiment of each of these reviews")
    positive_reviews = [doc for doc in doc_result if doc.sentiment == "positive"]
    mixed_reviews = [doc for doc in doc_result if doc.sentiment == "mixed"]
    negative_reviews = [doc for doc in doc_result if doc.sentiment == "negative"]
    print("...We have {} positive reviews, {} mixed reviews, and {} negative reviews. ".format(
        len(positive_reviews), len(mixed_reviews), len(negative_reviews)
    ))
    print(
        "\nSince these reviews seem so mixed, and since I'm interested in finding exactly what it is about my hotel that should be improved, "
        "let's find the complaints users have about individual aspects of this hotel"
    )

    print(
        "\nIn order to do that, I'm going to extract the targets of a negative sentiment. "
        "I'm going to map each of these targets to the mined opinion object we get back to aggregate the reviews by target. "
    )
    target_to_complaints = {}

    for document in doc_result:
        for sentence in document.sentences:
            for mined_opinion in sentence.mined_opinions:
                target = mined_opinion.target
                if target.sentiment == 'negative':
                    target_to_complaints.setdefault(target.text, [])
                    target_to_complaints[target.text].append(mined_opinion)

    print("\nLet's now go through the aspects of our hotel people have complained about and see what users have specifically said")

    for target, complaints in target_to_complaints.items():
        print("Users have made {} complaint(s) about '{}', specifically saying that it's '{}'".format(
            len(complaints),
            target,
            "', '".join(
                [assessment.text for complaint in complaints for assessment in complaint.assessments]
            )
        ))


    print(
        "\n\nLooking at the breakdown, I can see what aspects of my hotel need improvement, and based off of both the number and "
        "content of the complaints users have made about my toilets, I need to get that fixed ASAP."
    )


async def main():
    await sample_analyze_sentiment_with_opinion_mining()


if __name__ == '__main__':
    asyncio.run(main())
