# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_detailed_diagnostics_information_async.py

DESCRIPTION:
    This sample demonstrates how to retrieve batch statistics, the
    model version used, and the raw response returned from the service.

USAGE:
    python sample_get_detailed_diagnostics_information_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_ANALYTICS_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_TEXT_ANALYTICS_KEY - your Text Analytics subscription key
"""

import os
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class GetDetailedDiagnosticsInformationSampleAsync(object):

    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    async def get_detailed_diagnostics_information_async(self):
        from azure.ai.textanalytics.aio import TextAnalyticsClient
        from azure.ai.textanalytics import TextAnalyticsApiKeyCredential
        text_analytics_client = TextAnalyticsClient(endpoint=self.endpoint, credential=TextAnalyticsApiKeyCredential(self.key))

        documents = [
            "I had the best day of my life.",
            "This was a waste of my time. The speaker put me to sleep.",
            "No tengo dinero ni nada que dar...",
            "L'hôtel n'était pas très confortable. L'éclairage était trop sombre."
        ]

        def callback(resp):
            _LOGGER.info("document_count: {}".format(resp.statistics["document_count"]))
            _LOGGER.info("valid_document_count: {}".format(resp.statistics["valid_document_count"]))
            _LOGGER.info("erroneous_document_count: {}".format(resp.statistics["erroneous_document_count"]))
            _LOGGER.info("transaction_count: {}".format(resp.statistics["transaction_count"]))
            _LOGGER.info("model_version: {}".format(resp.model_version))
            _LOGGER.info("raw_response: {}".format(resp.raw_response))

        async with text_analytics_client:
            result = await text_analytics_client.analyze_sentiment(
                documents,
                show_stats=True,
                model_version="latest",
                raw_response_hook=callback
            )


async def main():
    sample = GetDetailedDiagnosticsInformationSampleAsync()
    await sample.get_detailed_diagnostics_information_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
