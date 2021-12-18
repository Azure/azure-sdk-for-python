# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from azure_devtools.perfstress_tests import PerfStressTest
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.formrecognizer.aio import DocumentAnalysisClient as AsyncDocumentAnalysisClient

class AnalyzeDocumentFromUrlRequestPreparation(PerfStressTest):   

    def __init__(self, arguments):
        super().__init__(arguments)

        self.document_jpg_url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Form_1.jpg"
        
        # read test related env vars
        formrecognizer_test_endpoint = os.environ["FORMRECOGNIZER_TEST_ENDPOINT"]
        form_recognizer_account_key = os.environ["FORMRECOGNIZER_TEST_API_KEY"]

        # assign the clients that will be used in the perf tests
        self.service_client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(form_recognizer_account_key))
        self.async_service_client = AsyncDocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(form_recognizer_account_key))

    async def close(self):
        """This is run after cleanup."""
        await self.async_service_client.close()
        self.service_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        poller = self.service_client.begin_analyze_document_from_url(
            "prebuilt-document",
            self.document_jpg_url)
        assert poller

    async def run_async(self):
        """The asynchronous perf test."""
        poller = await self.async_service_client.begin_analyze_document_from_url(
            "prebuilt-document",
            self.document_jpg_url)
        assert poller
