# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_detect_language.py

DESCRIPTION:
    This sample demonstrates how to detect language in a batch of different
    documents.

    In this sample, we own a hotel with a lot of international clientele. We
    are looking to catalog the reviews we have for our hotel by language, so
    we can translate these reviews into English.

USAGE:
    python sample_detect_language.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os


class DetectLanguageSample(object):

    def detect_language(self):
        print(
            "In this sample we own a hotel with customers from all around the globe. We want to eventually "
            "translate these reviews into English so our manager can read them. However, we first need to know which language "
            "they are in for more accurate translation. This is the step we will be covering in this sample\n"
        )
        # [START detect_language]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        documents = [
            """
            The concierge Paulette was extremely helpful. Sadly when we arrived the elevator was broken, but with Paulette's help we barely noticed this inconvenience.
            She arranged for our baggage to be brought up to our room with no extra charge and gave us a free meal to refurbish all of the calories we lost from
            walking up the stairs :). Can't say enough good things about my experience!
            """,
            """
            最近由于工作压力太大，我们决定去富酒店度假。那儿的温泉实在太舒服了，我跟我丈夫都完全恢复了工作前的青春精神！加油！
            """
        ]

        result = text_analytics_client.detect_language(documents)
        reviewed_docs = [doc for doc in result if not doc.is_error]

        print("Let's see what language each review is in!")

        for idx, doc in enumerate(reviewed_docs):
            print("Review #{} is in '{}', which has ISO639-1 name '{}'\n".format(
                idx, doc.primary_language.name, doc.primary_language.iso6391_name
            ))
            if doc.is_error:
                print(doc.id, doc.error)
        # [END detect_language]
        print(
            "When actually storing the reviews, we want to map the review to their ISO639-1 name "
            "so everything is more standardized"
        )

        review_to_language = {}
        for idx, doc in enumerate(reviewed_docs):
            review_to_language[documents[idx]] = doc.primary_language.iso6391_name


if __name__ == '__main__':
    sample = DetectLanguageSample()
    sample.detect_language()
