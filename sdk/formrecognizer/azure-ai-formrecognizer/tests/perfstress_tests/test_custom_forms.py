# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import functools
from io import BytesIO
from datetime import date, time
from azure_devtools.perfstress_tests import PerfStressTest
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient, FormContentType
from azure.ai.formrecognizer.aio import FormRecognizerClient as AsyncFormRecognizerClient

class TestCustomForms(PerfStressTest):   

    def __init__(self, arguments):
        super().__init__(arguments)

        with open(os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./../sample_forms/forms/Form_1.jpg")), "rb") as fd:
            self.custom_form_jpg = fd.read()
        
        # read test related env vars
        formrecognizer_storage_container_sas_url = os.environ["FORMRECOGNIZER_TESTING_DATA_CONTAINER_SAS_URL"]
        formrecognizer_test_endpoint = os.environ["FORMRECOGNIZER_TEST_ENDPOINT"]
        form_recognizer_account_key = os.environ["FORMRECOGNIZER_TEST_API_KEY"]

        # assign the clients that will be used in the perf tests
        self.service_client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(form_recognizer_account_key))
        self.async_service_client = AsyncFormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(form_recognizer_account_key))

        # train a model for the test
        training_client = FormTrainingClient(formrecognizer_test_endpoint, AzureKeyCredential(form_recognizer_account_key))
        poller = training_client.begin_training(
            formrecognizer_storage_container_sas_url, 
            use_training_labels=False, 
            model_name="unlabeled")
        model = poller.result()
        self.model_id = model.model_id

    async def close(self):
        """This is run after cleanup."""
        await self.async_service_client.close()
        self.service_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test."""
        poller = self.service_client.begin_recognize_custom_forms(
            self.model_id, 
            self.custom_form_jpg, 
            content_type=FormContentType.IMAGE_JPEG)
        result = poller.result()
        if result is not None:
            pass

    async def run_async(self):
        """The asynchronous perf test."""
        poller = await self.async_service_client.begin_recognize_custom_forms(
            self.model_id, 
            self.custom_form_jpg,
            content_type=FormContentType.IMAGE_JPEG)
        result = await poller.result()
        if result is not None:
            pass
