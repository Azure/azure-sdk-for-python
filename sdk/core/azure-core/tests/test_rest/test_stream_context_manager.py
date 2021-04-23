# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import mock
from azure.core.rest import HttpRequest, ResponseNotReadError
from azure.core.exceptions import HttpResponseError
try:
    from azure.core.rest._rest_py3 import _StreamContextManager
except (ImportError, SyntaxError):
    from azure.core.rest._rest import _StreamContextManager

from azure.core.pipeline import Pipeline, transport
from azure.core.pipeline.transport import RequestsTransport

def test_stream_context_manager():
    transport = mock.MagicMock()
    pipeline = Pipeline(transport=transport)
    with _StreamContextManager(pipeline=pipeline, request=HttpRequest(method="GET", url="https://httpbin.org/get")) as r:
        response = r

        assert len(transport.method_calls) == 1
        method_call = transport.method_calls[0]
        assert method_call[0] == 'send'  # check method call name

        assert len(method_call[1])  # assert args
        arg = method_call[1][0]
        assert arg.url == "https://httpbin.org/get"
        assert arg.method == "GET"

        assert method_call[2] == {"stream": True}  # check kwargs

    # assert actual response from requests etc is closed
    internal_response_mock_calls = response._internal_response.internal_response.mock_calls
    assert len(internal_response_mock_calls) == 1
    assert internal_response_mock_calls[0][0] == '__exit__'  # assert exit was called

def test_stream_context_manager_error():
    pipeline = Pipeline(transport=RequestsTransport())
    with _StreamContextManager(pipeline=pipeline, request=HttpRequest(method="GET", url="https://httpbin.org/status/404")) as r:
        with pytest.raises(HttpResponseError) as e:
            r.raise_for_status()
        assert e.value.status_code == 404
        assert e.value.reason == "NOT FOUND"
        with pytest.raises(ResponseNotReadError):
            str(e.value)  # str should not fail. Probably don't show body in str
            e.value.response.json()
        with pytest.raises(ResponseNotReadError):
            r.json()
        with pytest.raises(ResponseNotReadError):
            r.content
        r.read()
        assert str(e.value) == "HttpResponseError: 404 NOT FOUND"
        assert r.content == b''
    assert r.is_closed
    assert r.is_stream_consumed
