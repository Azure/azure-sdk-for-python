# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_recognize_pii_entities_async.py

DESCRIPTION:
    This sample demonstrates how to recognize personally identifiable
    information in a single string. For the list of supported entity types,
    see https://aka.ms/tanerpii

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_recognize_pii_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Entity: 111000025
    Type: ABA Routing Number
    Confidence Score: 0.75

    Entity: 555-55-5555
    Type: U.S. Social Security Number (SSN)
    Confidence Score: 0.85
"""

import os
import asyncio


class SingleRecognizePiiEntitiesSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def recognize_pii_entities_async(self):
        # [START single_recognize_pii_entities_async]
        from azure.ai.textanalytics.aio import single_recognize_pii_entities
        from azure.ai.textanalytics import TextAnalyticsSubscriptionKeyCredential

        text = "The employee's ABA number is 111000025 and his SSN is 555-55-5555."

        result = await single_recognize_pii_entities(
            endpoint=self.endpoint,
            credential=TextAnalyticsSubscriptionKeyCredential(self.key),
            input_text=text,
            language="en"
        )

        for entity in result.entities:
            print("Entity: {}".format(entity.text))
            print("Type: {}".format(entity.type))
            print("Confidence Score: {}\n".format(entity.score))
        # [END single_recognize_pii_entities_async]


async def main():
    sample = SingleRecognizePiiEntitiesSampleAsync()
    await sample.recognize_pii_entities_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
