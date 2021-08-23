# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import pytest
import json
try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore

from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
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

    @FormRecognizerPreparer()
    def test_mock_quota_exceeded_403(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):

        response = mock.Mock(
            status_code=403,
            headers={"Retry-After": 186688, "Content-Type": "application/json"},
            reason="Bad Request"
        )
        response.text = lambda encoding=None: json.dumps(
            {"error": {"code": "403", "message": "Out of call volume quota for FormRecognizer F0 pricing tier. "
            "Please retry after 1 day. To increase your call volume switch to a paid tier."}}
        )
        response.content_type = "application/json"
        transport = mock.Mock(send=lambda request, **kwargs: response)

        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), transport=transport)

        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg)
        assert e.value.status_code == 403
        assert e.value.error.message == 'Out of call volume quota for FormRecognizer F0 pricing tier. Please retry after 1 day. To increase your call volume switch to a paid tier.'

    @FormRecognizerPreparer()
    def test_mock_quota_exceeded_429(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):

        response = mock.Mock(
            status_code=429,
            headers={"Retry-After": 186688, "Content-Type": "application/json"},
            reason="Bad Request"
        )
        response.text = lambda encoding=None: json.dumps(
            {"error": {"code": "429", "message": "Out of call volume quota for FormRecognizer F0 pricing tier. "
            "Please retry after 1 day. To increase your call volume switch to a paid tier."}}
        )
        response.content_type = "application/json"
        transport = mock.Mock(send=lambda request, **kwargs: response)

        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), transport=transport)

        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg)
        assert e.value.status_code == 429
        assert e.value.error.message == 'Out of call volume quota for FormRecognizer F0 pricing tier. Please retry after 1 day. To increase your call volume switch to a paid tier.'
