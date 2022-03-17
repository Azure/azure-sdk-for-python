# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure_devtools.perfstress_tests import PerfStressTest
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.textanalytics.aio import TextAnalyticsClient as AsyncTextAnalyticsClient

class DetectLanguagePerfStressTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # test related env vars
        endpoint = os.environ["AZURE_TEXT_ANALYTICS_ENDPOINT"]
        key = os.environ["AZURE_TEXT_ANALYTICS_KEY"]

        # assign the clients that will be used in the perf tests
        self.service_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )
        self.async_service_client = AsyncTextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )
        self.input = ["Detta är ett dokument skrivet på engelska."] * 1000

    async def close(self):
        """This is run after cleanup."""
        await self.async_service_client.close()
        self.service_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        self.service_client.detect_language(self.input)

    async def run_async(self):
        """The asynchronous perf test."""
        await self.async_service_client.detect_language(self.input)
