# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_single_extract_key_phrases_async.py

DESCRIPTION:
    This sample demonstrates how to extract key phrases from a single string.

    This module-level, single method is meant to be used as an introduction
    for new users of the text analytics service. For optimum use of the service,
    use the methods that support batching documents.

USAGE:
    python sample_single_extract_key_phrases_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your cognitive services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your text analytics subscription key

OUTPUT:
    Key phrases found:

    King County
    United States
    Washington
    city
    miles
    Redmond
    Seattle
"""

import os
import asyncio


class SingleExtractKeyPhrasesSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def extract_key_phrases_async(self):
        # [START single_extract_key_phrases_async]
        from azure.ai.textanalytics.aio import single_extract_key_phrases

        text = "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle."

        result = await single_extract_key_phrases(
            endpoint=self.endpoint,
            credential=self.key,
            input_text=text,
            language="en"
        )

        print("Key phrases found:\n")
        for phrase in result.key_phrases:
            print(phrase)
        # [END single_extract_key_phrases_async]


async def main():
    sample = SingleExtractKeyPhrasesSampleAsync()
    await sample.extract_key_phrases_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
