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

    In this sample, we want to go over articles and read the ones that mention Microsoft.
    We're going to use the SDK to create a rudimentary search algorithm to find these articles.

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
        print(
            "In this sample, we want to find the articles that mention Microsoft to read."
        )
        articles_that_mention_microsoft = []
        # [START extract_key_phrases_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import TextAnalyticsClient

        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        articles = [
            """
            Washington, D.C. Autumn in DC is a uniquely beautiful season. The leaves fall from the trees
            in a city chockful of forrests, leaving yellow leaves on the ground and a clearer view of the
            blue sky above...
            """,
            """
            Redmond, WA. In the past few days, Microsoft has decided to further postpone the start date of
            its United States workers, due to the pandemic that rages with no end in sight...
            """,
            """
            Redmond, WA. Employees at Microsoft can be excited about the new coffee shop that will open on campus
            once workers no longer have to work remotely...
            """
        ]

        async with text_analytics_client:
            result = await text_analytics_client.extract_key_phrases(articles)

        for idx, doc in enumerate(result):
            if not doc.is_error:
                print("Key phrases in article #{}: {}".format(
                    idx + 1,
                    ", ".join(doc.key_phrases)
                ))
        # [END extract_key_phrases_async]
                if "Microsoft" in doc.key_phrases:
                    articles_that_mention_microsoft.append(str(idx + 1))

        print(
            "The articles that mention Microsoft are articles number: {}. Those are the ones I'm interested in reading.".format(
                ", ".join(articles_that_mention_microsoft)
            )
        )


async def main():
    sample = ExtractKeyPhrasesSampleAsync()
    await sample.extract_key_phrases_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
