# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_detect_language_async.py

DESCRIPTION:
    This sample demonstrates how to detect language in a batch of different
    documents.

USAGE:
    python sample_detect_language_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key
"""

import os
import asyncio


class DetectLanguageSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def detect_language_async(self):
        # [START batch_detect_language_async]
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))
        documents = [
            "This document is written in English.",
            "Este es un document escrito en Español.",
            "这是一个用中文写的文件",
            "Dies ist ein Dokument in englischer Sprache.",
            "Detta är ett dokument skrivet på engelska."
        ]
        async with text_analytics_client:
            result = await text_analytics_client.detect_language(documents)

        for idx, doc in enumerate(result):
            if not doc.is_error:
                print("Document text: {}".format(documents[idx]))
                print("Language detected: {}".format(doc.primary_language.name))
                print("ISO6391 name: {}".format(doc.primary_language.iso6391_name))
                print("Confidence score: {}\n".format(doc.primary_language.score))
            if doc.is_error:
                print(doc.id, doc.error)
        # [END batch_detect_language_async]

    async def alternative_scenario_detect_language_async(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[DetectLanguageInput] and supplying your own IDs and country hints along
        with the text.
        """
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))

        documents = [
            {"id": "0", "country_hint": "US", "text": "This is a document written in English."},
            {"id": "1", "country_hint": "MX", "text": "Este es un document escrito en Español."},
            {"id": "2", "country_hint": "CN", "text": "这是一个用中文写的文件"},
            {"id": "3", "country_hint": "DE", "text": "Dies ist ein Dokument in englischer Sprache."},
            {"id": "4", "country_hint": "SE",  "text": "Detta är ett dokument skrivet på engelska."}
        ]

        extras = []

        def callback(resp):
            extras.append(resp.statistics)
            extras.append(resp.model_version)
            extras.append(resp.raw_response)

        async with text_analytics_client:
            result = await text_analytics_client.detect_language(
                documents,
                show_stats=True,
                model_version="latest",
                response_hook=callback
            )


async def main():
    sample = DetectLanguageSampleAsync()
    await sample.detect_language_async()
    await sample.alternative_scenario_detect_language_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
