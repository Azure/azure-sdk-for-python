# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import pytest
import json
import sys
import asyncio
import functools
from unittest import mock
from azure.ai.formrecognizer.aio import DocumentAnalysisClient, DocumentModelAdministrationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from preparers import FormRecognizerPreparer, get_async_client
from asynctestcase import AsyncFormRecognizerTest


class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


def get_completed_future(result=None):
    future = asyncio.Future()
    future.set_result(result)
    return future


def wrap_in_future(fn):
    """Return a completed Future whose result is the return of fn.
    Added to simplify using unittest.Mock in async code. Python 3.8's AsyncMock would be preferable.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        return get_completed_future(result)
    return wrapper


class AsyncMockTransport(mock.MagicMock):
    """Mock with do-nothing aenter/exit for mocking async transport.

    This is unnecessary on 3.8+, where MagicMocks implement aenter/exit.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if sys.version_info < (3, 8):
            self.__aenter__ = mock.Mock(return_value=get_completed_future())
            self.__aexit__ = mock.Mock(return_value=get_completed_future())


class TestLogging(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_mock_quota_exceeded_403(self, **kwargs):
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
        transport = AsyncMockTransport(send=wrap_in_future(lambda request, **kwargs: response))

        client = get_async_client(DocumentAnalysisClient, transport=transport)

        with pytest.raises(HttpResponseError) as e:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)
        assert e.value.status_code == 403
        assert e.value.error.message == 'Out of call volume quota for FormRecognizer F0 pricing tier. Please retry after 1 day. To increase your call volume switch to a paid tier.'

    @FormRecognizerPreparer()
    async def test_mock_quota_exceeded_429(self, **kwargs):
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
        transport = AsyncMockTransport(send=wrap_in_future(lambda request, **kwargs: response))

        client = get_async_client(DocumentAnalysisClient, transport=transport)
        with pytest.raises(HttpResponseError) as e:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)
        assert e.value.status_code == 429
        assert e.value.error.message == 'Out of call volume quota for FormRecognizer F0 pricing tier. Please retry after 1 day. To increase your call volume switch to a paid tier.'
