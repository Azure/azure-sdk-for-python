# coding=utf-8
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
        self.textanalytics_test_endpoint = os.environ["TEXTANALYTICS_TEST_ENDPOINT"]
        self.textanalytics_test_api_key = os.environ["TEXTANALYTICS_TEST_API_KEY"]

        # assign the clients that will be used in the perf tests
