# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from azure_devtools.perfstress_tests import PerfStressTest
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentModelAdministrationClient
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient as AsyncDocumentModelAdministrationClient

class BuildModelRequestPreparation(PerfStressTest):   

    def __init__(self, arguments):
        super().__init__(arguments)

        # read test related env vars
        self.formrecognizer_storage_container_sas_url = os.environ["FORMRECOGNIZER_TRAINING_DATA_CONTAINER_SAS_URL"]
        formrecognizer_test_endpoint = os.environ["FORMRECOGNIZER_TEST_ENDPOINT"]
        form_recognizer_account_key = os.environ["FORMRECOGNIZER_TEST_API_KEY"]

        # assign the clients that will be used in the perf tests
        self.admin_client = DocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential(form_recognizer_account_key))
        self.async_admin_client = AsyncDocumentModelAdministrationClient(formrecognizer_test_endpoint, AzureKeyCredential(form_recognizer_account_key))

    async def close(self):
        """This is run after cleanup."""
        await self.async_admin_client.close()
        self.admin_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        poller = self.admin_client.begin_build_model("template", blob_container_url=self.formrecognizer_storage_container_sas_url)
        assert poller

    async def run_async(self):
        """The asynchronous perf test."""
        poller = await self.async_admin_client.begin_build_model("template", blob_container_url=self.formrecognizer_storage_container_sas_url)
        assert poller
