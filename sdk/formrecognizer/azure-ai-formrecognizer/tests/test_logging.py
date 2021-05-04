# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import pytest
from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from testcase import FormRecognizerTest
from preparers import FormRecognizerPreparer

class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class TestLogging(FormRecognizerTest):

    @FormRecognizerPreparer()
    @pytest.mark.live_test_only
    def test_logging_info_fr_client(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.INFO)

        poller = client.begin_recognize_invoices_from_url(self.receipt_url_jpg)
        result = poller.result()

        for message in mock_handler.messages:
            if message.levelname == "INFO":
                # not able to use json.loads here. At INFO level only API key should be REDACTED
                if message.message.find("Ocp-Apim-Subscription-Key") != -1:
                    assert message.message.find("REDACTED") != -1
                else:
                    assert message.message.find("REDACTED") == -1

    @FormRecognizerPreparer()
    @pytest.mark.live_test_only
    def test_logging_info_ft_client(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormTrainingClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.INFO)

        result = client.get_account_properties()

        for message in mock_handler.messages:
            if message.levelname == "INFO":
                # not able to use json.loads here. At INFO level only API key should be REDACTED
                if message.message.find("Ocp-Apim-Subscription-Key") != -1:
                    assert message.message.find("REDACTED") != -1
                else:
                    assert message.message.find("REDACTED") == -1
