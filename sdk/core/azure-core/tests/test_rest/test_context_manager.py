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
    from azure.core.rest._rest_py3 import _SyncContextManager
except (ImportError, SyntaxError):
    from azure.core.rest._rest import _SyncContextManager

from azure.core.pipeline import Pipeline, transport
from azure.core.pipeline.transport import RequestsTransport

# def test_normal_call(client):
#     request = HttpRequest("GET", url="http://127.0.0.1:5000/basic/string")
#     with client.send_request(request) as response:
#         response.raise_for_status()
#         assert response.text == "Hello, world!"

#     response = client.send_request(request)
#     response.raise_for_status()
#     assert response.text == "Hello, world!"


# def test_stream_context_manager():
#     transport = mock.MagicMock()
#     pipeline = Pipeline(transport=transport)
#     with _SyncContextManager(pipeline=pipeline, request=HttpRequest(method="GET", url="https://httpbin.org/get")) as r:
#         response = r

#         assert len(transport.method_calls) == 1
#         method_call = transport.method_calls[0]
#         assert method_call[0] == 'send'  # check method call name

#         assert len(method_call[1])  # assert args
#         arg = method_call[1][0]
#         assert arg.url == "https://httpbin.org/get"
#         assert arg.method == "GET"

#         assert method_call[2] == {"stream": True}  # check kwargs

#     # assert actual response from requests etc is closed
#     internal_response_mock_calls = response._internal_response.internal_response.mock_calls
#     assert len(internal_response_mock_calls) == 1
#     assert internal_response_mock_calls[0][0] == '__exit__'  # assert exit was called

# def test_stream_context_manager_error():
#     pipeline = Pipeline(transport=RequestsTransport())
#     with _SyncContextManager(pipeline=pipeline, request=HttpRequest(method="GET", url="http://localhost:3000/errors/stream")) as r:
#         with pytest.raises(HttpResponseError) as e:
#             r.raise_for_status()
#         assert e.value.status_code == 404
#         assert e.value.reason == "NOT FOUND"
#         with pytest.raises(ResponseNotReadError):
#             str(e.value)  # str should not fail. Probably don't show body in str
#             e.value.response.json()
#         with pytest.raises(ResponseNotReadError):
#             r.json()
#         with pytest.raises(ResponseNotReadError):
#             r.content
#         r.read()
#         assert str(e.value) == "Operation returned an invalid status 'NOT FOUND'"
#         assert r.content == b''
#     assert r.is_closed
#     assert r.is_stream_consumed

def test_stream_with_error(client):
    request = HttpRequest("GET", url="http://127.0.0.1:5000/streams/error")
    with client.send_request(request, stream=True) as response:
        assert not response.is_closed
        with pytest.raises(HttpResponseError) as e:
            response.raise_for_status()
        error = e.value
        assert error.status_code == 400
        assert error.reason == "BAD REQUEST"
        assert "Operation returned an invalid status 'BAD REQUEST'" in str(error)
        with pytest.raises(ResponseNotReadError):
            error.error
        with pytest.raises(ResponseNotReadError):
            error.model
        with pytest.raises(ResponseNotReadError):
            response.json()
        with pytest.raises(ResponseNotReadError):
            response.content

        # NOW WE READ THE RESPONSE
        response.read()
        assert error.status_code == 400
        assert error.reason == "BAD REQUEST"
        assert error.error.code == "BadRequest"
        assert error.error.message == "You made a bad request"
        assert error.model.code == "BadRequest"
        assert error.error.message == "You made a bad request"