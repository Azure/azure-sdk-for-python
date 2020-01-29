# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_recognize_entities_async.py

DESCRIPTION:
    This sample demonstrates how to recognize entities in a single string.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_recognize_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Entity: Microsoft
    Category: Organization
    Confidence Score: 1.000

    Entity: Bill Gates
    Category: Person
    Confidence Score: 1.000

    Entity: Paul Allen
    Category: Person
    Confidence Score: 0.999

    Entity: April 4, 1975
    Category: DateTime
    Confidence Score: 0.800

    Entity: Altair
    Category: Organization
    Confidence Score: 0.525

    Entity: 8800
    Category: Quantity
    Confidence Score: 0.80
"""

import os
import asyncio


class SingleRecognizeEntitiesSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def recognize_entities_async(self):
        # [START single_recognize_entities_async]
        from azure.ai.textanalytics.aio import single_recognize_entities
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential

        text = "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975," \
               " to develop and sell BASIC interpreters for the Altair 8800."

        result = await single_recognize_entities(
            endpoint=self.endpoint,
            credential=TextAnalyticsApiKeyCredential(self.key),
            input_text=text,
            language="en"
        )

        for entity in result.entities:
            print("Entity: {}".format(entity.text))
            print("Category: {}".format(entity.category))
            print("Confidence Score: {0:.3f}\n".format(entity.score))
        # [END single_recognize_entities_async]


async def main():
    sample = SingleRecognizeEntitiesSampleAsync()
    await sample.recognize_entities_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
