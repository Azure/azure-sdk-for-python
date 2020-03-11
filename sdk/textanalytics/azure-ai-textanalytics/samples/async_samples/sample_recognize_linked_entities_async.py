# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_linked_entities_async.py

DESCRIPTION:
    This sample demonstrates how to detect linked entities in a batch of documents.
    Each entity found in the document will have a link associated with it from a
    data source.

USAGE:
    python sample_recognize_linked_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os
import asyncio


class RecognizeLinkedEntitiesSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def recognize_linked_entities_async(self):
        # [START batch_recognize_linked_entities_async]
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))
        documents = [
            "Microsoft moved its headquarters to Bellevue, Washington in January 1979.",
            "Steve Ballmer stepped down as CEO of Microsoft and was succeeded by Satya Nadella.",
            "Microsoft superó a Apple Inc. como la compañía más valiosa que cotiza en bolsa en el mundo.",
        ]

        async with text_analytics_client:
            result = await text_analytics_client.recognize_linked_entities(documents)

        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            print("Document text: {}\n".format(documents[idx]))
            for entity in doc.entities:
                print("Entity: {}".format(entity.name))
                print("Url: {}".format(entity.url))
                print("Data Source: {}".format(entity.data_source))
                for match in entity.matches:
                    print("Confidence Score: {}".format(match.score))
                    print("Entity as appears in request: {}".format(match.text))
            print("------------------------------------------")
        # [END batch_recognize_linked_entities_async]


async def main():
    sample = RecognizeLinkedEntitiesSampleAsync()
    await sample.recognize_linked_entities_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
