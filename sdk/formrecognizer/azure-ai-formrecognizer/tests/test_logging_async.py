# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import pytest
from azure.ai.formrecognizer.aio import FormRecognizerClient, FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from testcase import GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest


class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class TestLogging(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    @pytest.mark.live_test_only
    async def test_logging_info_fr_client(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.INFO)
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.receipt_url_jpg)
            result = await poller.result()

        for message in mock_handler.messages:
            if message.levelname == "INFO":
                # not able to use json.loads here. At INFO level only API key should be REDACTED
                if message.message.find("Ocp-Apim-Subscription-Key") != -1:
                    assert message.message.find("REDACTED") != -1
                else:
                    assert message.message.find("REDACTED") == -1

    @GlobalFormRecognizerAccountPreparer()
    @pytest.mark.live_test_only
    async def test_logging_info_ft_client(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormTrainingClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.INFO)
        async with client:
            result = await client.get_account_properties()

        for message in mock_handler.messages:
            if message.levelname == "INFO":
                # not able to use json.loads here. At INFO level only API key should be REDACTED
                if message.message.find("Ocp-Apim-Subscription-Key") != -1:
                    assert message.message.find("REDACTED") != -1
                else:
                    assert message.message.find("REDACTED") == -1
