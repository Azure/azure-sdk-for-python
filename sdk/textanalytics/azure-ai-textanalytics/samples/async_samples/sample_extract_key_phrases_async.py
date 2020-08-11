# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_extract_key_phrases_async.py

DESCRIPTION:
    This sample demonstrates how to extract key talking points from a batch of documents.

USAGE:
    python sample_extract_key_phrases_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os
import asyncio


class ExtractKeyPhrasesSampleAsync(object):

    async def extract_key_phrases_async(self):
        # [START extract_key_phrases_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        documents = [
            "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
            "I need to take my cat to the veterinarian.",
            "I will travel to South America in the summer.",
        ]

        async with text_analytics_client:
            result = await text_analytics_client.extract_key_phrases(documents)

        for doc in result:
            if not doc.is_error:
                print(doc.key_phrases)
            if doc.is_error:
                print(doc.id, doc.error)
        # [END extract_key_phrases_async]


async def main():
    sample = ExtractKeyPhrasesSampleAsync()
    await sample.extract_key_phrases_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
