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
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key
"""

import os
import asyncio


class ExtractKeyPhrasesSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def extract_key_phrases_async(self):
        # [START batch_extract_key_phrases_async]
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))
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
        # [END batch_extract_key_phrases_async]

    async def alternative_scenario_extract_key_phrases_async(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[TextDocumentInput] and supplying your own IDs and language hints along
        with the text.
        """
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))

        documents = [
            {"id": "0", "language": "en",
             "text": "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle."},
            {"id": "1", "language": "en",
                "text": "I need to take my cat to the veterinarian."},
            {"id": "2", "language": "en", "text": "I will travel to South America in the summer."}
        ]
        extras = []

        def callback(resp):
            extras.append(resp.statistics)
            extras.append(resp.model_version)
            extras.append(resp.raw_response)

        async with text_analytics_client:
            result = await text_analytics_client.extract_key_phrases(
                documents,
                show_stats=True,
                model_version="latest",
                response_hook=callback
            )


async def main():
    sample = ExtractKeyPhrasesSampleAsync()
    await sample.extract_key_phrases_async()
    await sample.alternative_scenario_extract_key_phrases_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
