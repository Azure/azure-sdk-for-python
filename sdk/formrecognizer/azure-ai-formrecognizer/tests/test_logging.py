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

from azure.ai.formrecognizer import DocumentAnalysisClient, DocumentModelAdministrationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from testcase import FormRecognizerTest
from preparers import FormRecognizerPreparer, get_sync_client

class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class TestLogging(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_mock_quota_exceeded_403(self, **kwargs):
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

        client = get_sync_client(DocumentAnalysisClient, transport=transport)

        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)
        assert e.value.status_code == 403
        assert e.value.error.message == 'Out of call volume quota for FormRecognizer F0 pricing tier. Please retry after 1 day. To increase your call volume switch to a paid tier.'

    @FormRecognizerPreparer()
    def test_mock_quota_exceeded_429(self, **kwargs):
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

        client = get_sync_client(DocumentAnalysisClient, transport=transport)

        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)
        assert e.value.status_code == 429
        assert e.value.error.message == 'Out of call volume quota for FormRecognizer F0 pricing tier. Please retry after 1 day. To increase your call volume switch to a paid tier.'
