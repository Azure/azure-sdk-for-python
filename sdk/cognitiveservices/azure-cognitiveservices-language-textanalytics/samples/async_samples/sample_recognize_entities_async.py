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
    2) AZURE_COGNITIVE_SERVICES_KEY - your cognitive services account key

OUTPUT:
    Document text: Microsoft was founded by Bill Gates and Paul Allen.
    Entity:          Microsoft      Type:    Organization   Confidence Score:        0.99993896484375
    Entity:          Bill Gates     Type:    Person         Confidence Score:        0.9997406601905823
    Entity:          Paul Allen     Type:    Person         Confidence Score:        0.9995118379592896

    Document text: Microsoft wurde von Bill Gates und Paul Allen gegründet.
    Entity:          Microsoft      Type:    Organization   Confidence Score:        0.9998779296875
    Entity:          Bill Gates     Type:    Person         Confidence Score:        0.7356343269348145
    Entity:          Paul Allen     Type:    Person         Confidence Score:        0.914785623550415

    Document text: Microsoft fue fundado por Bill Gates y Paul Allen.
    Entity:          Microsoft      Type:    Organization   Confidence Score:        0.9999008178710938
    Entity:          Bill Gates     Type:    Person         Confidence Score:        0.9996491074562073
    Entity:          Paul Allen     Type:    Person         Confidence Score:        0.9989705681800842

    Document text: Microsoft a été fondée par Bill Gates et Paul Allen.
    Entity:          Microsoft      Type:    Organization   Confidence Score:        0.99993896484375
    Entity:          Bill Gates     Type:    Person         Confidence Score:        0.9985819458961487
    Entity:          Paul Allen     Type:    Person         Confidence Score:        0.9499356150627136
"""

import os
import asyncio


class RecognizeEntitiesSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_COGNITIVE_SERVICES_KEY")

    async def recognize_entities_async(self):
        from azure.cognitiveservices.language.textanalytics.aio import TextAnalyticsClient
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=self.key)
        documents = [
            "Microsoft was founded by Bill Gates and Paul Allen.",
            "Microsoft wurde von Bill Gates und Paul Allen gegründet.",
            "Microsoft fue fundado por Bill Gates y Paul Allen.",
            "Microsoft a été fondée par Bill Gates et Paul Allen.",
        ]

        async with text_analytics_client:
            result = await text_analytics_client.recognize_entities(documents)

        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("\nDocument text: {}".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: \t", entity.text, "\tType: \t", entity.type, "\tConfidence Score: \t", entity.score)

    async def advanced_scenario_recognize_entities_async(self):
        """This sample demonstrates how to retrieve batch statistics, the
        model version used, and the raw response returned from the service.

        It additionally shows an alternative way to pass in the input documents
        using a list[MultiLanguageInput] and supplying your own IDs and language hints along
        with the text.
        """
        from azure.cognitiveservices.language.textanalytics.aio import TextAnalyticsClient
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=self.key)

        documents = [
            {"id": "0", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            {"id": "1", "language": "de", "text": "Microsoft wurde von Bill Gates und Paul Allen gegründet."},
            {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen."},
            {"id": "3", "language": "fr", "text": "Microsoft a été fondée par Bill Gates et Paul Allen."}
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
    await sample.advanced_scenario_recognize_entities_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
