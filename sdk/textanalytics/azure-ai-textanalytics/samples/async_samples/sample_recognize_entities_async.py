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
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Document text: Microsoft was founded by Bill Gates and Paul Allen.
    Entity:          Microsoft      Type:    Organization   Confidence Score:        1.0
    Entity:          Bill Gates     Type:    Person         Confidence Score:        1.0
    Entity:          Paul Allen     Type:    Person         Confidence Score:        1.0

    Document text: I had a wonderful trip to Seattle last week.
    Entity:          Seattle        Type:    Location       Confidence Score:        0.806
    Entity:          last week      Type:    DateTime       Confidence Score:        0.8

    Document text: I visited the Space Needle 2 times.
    Entity:          Space Needle   Type:    Organization   Confidence Score:        0.922
    Entity:          2              Type:    Quantity       Confidence Score:        0.8

"""

import os
import asyncio


class RecognizeEntitiesSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def recognize_entities_async(self):
        # [START batch_recognize_entities_async]
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsAPIKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsAPIKeyCredential(self.key))
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
                print("Entity: \t", entity.name, "\tType: \t", entity.type,
                      "\tConfidence Score: \t", round(entity.score, 3))
        # [END batch_recognize_entities_async]

    async def alternative_scenario_recognize_entities_async(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[TextDocumentInput] and supplying your own IDs and language hints along
        with the text.
        """
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsAPIKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsAPIKeyCredential(self.key))

        documents = [
            {"id": "0", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            {"id": "1", "language": "de", "text": "I had a wonderful trip to Seattle last week."},
            {"id": "2", "language": "es", "text": "I visited the Space Needle 2 times."},
        ]

        extras = []

        def callback(resp):
            extras.append(resp.statistics)
            extras.append(resp.model_version)
            extras.append(resp.raw_response)

        async with text_analytics_client:
            result = await text_analytics_client.recognize_entities(
                documents,
                show_stats=True,
                model_version="latest",
                response_hook=callback
            )


async def main():
    sample = RecognizeEntitiesSampleAsync()
    await sample.recognize_entities_async()
    await sample.alternative_scenario_recognize_entities_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
