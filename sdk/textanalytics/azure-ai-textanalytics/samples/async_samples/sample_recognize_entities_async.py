# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_entities_async.py

DESCRIPTION:
    This sample demonstrates how to recognize named entities in a batch of documents.

USAGE:
    python sample_recognize_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os
import asyncio


class RecognizeEntitiesSampleAsync(object):

    endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
    key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

    async def recognize_entities_async(self):
        # [START batch_recognize_entities_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        documents = [
            "Microsoft was founded by Bill Gates and Paul Allen.",
            "I had a wonderful trip to Seattle last week.",
            "I visited the Space Needle 2 times.",
        ]

        async with text_analytics_client:
            result = await text_analytics_client.recognize_entities(documents)

        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("\nDocument text: {}".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: \t", entity.text, "\tCategory: \t", entity.category,
                      "\tConfidence Score: \t", entity.confidence_score)
        # [END batch_recognize_entities_async]


async def main():
    sample = RecognizeEntitiesSampleAsync()
    await sample.recognize_entities_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
