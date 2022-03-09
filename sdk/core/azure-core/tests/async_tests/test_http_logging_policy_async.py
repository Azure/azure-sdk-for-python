# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the HttpLoggingPolicy."""

import logging
import types
import pytest
import sys
from unittest.mock import Mock
from azure.core.pipeline import (
    PipelineResponse,
    PipelineRequest,
    PipelineContext
)
from azure.core.pipeline.policies import (
    HttpLoggingPolicy,
)
from utils import HTTP_RESPONSES, request_and_responses_product, create_http_response

@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_http_logger(http_request, http_response):

    class MockHandler(logging.Handler):
        def __init__(self):
            super(MockHandler, self).__init__()
            self.messages = []
        def reset(self):
            self.messages = []
        def emit(self, record):
            self.messages.append(record)
    mock_handler = MockHandler()

    logger = logging.getLogger("testlogger")
    logger.addHandler(mock_handler)
    logger.setLevel(logging.DEBUG)

    policy = HttpLoggingPolicy(logger=logger)

    universal_request = http_request('GET', 'http://localhost/')
    http_response = create_http_response(http_response, universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None))

    # Basics

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 2
    messages_request = mock_handler.messages[0].message.split("\n")
    messages_response = mock_handler.messages[1].message.split("\n")
    assert messages_request[0] == "Request URL: 'http://localhost/'"
    assert messages_request[1] == "Request method: 'GET'"
    assert messages_request[2] == 'Request headers:'
    assert messages_request[3] == 'No body was attached to the request'
    assert messages_response[0] == 'Response status: 202'
    assert messages_response[1] == 'Response headers:'

    mock_handler.reset()

    # Let's make this request a failure, retried twice

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 4
    messages_request1 = mock_handler.messages[0].message.split("\n")
    messages_response1 = mock_handler.messages[1].message.split("\n")
    messages_request2 = mock_handler.messages[2].message.split("\n")
    messages_response2 = mock_handler.messages[3].message.split("\n")
    assert messages_request1[0] == "Request URL: 'http://localhost/'"
    assert messages_request1[1] == "Request method: 'GET'"
    assert messages_request1[2] == 'Request headers:'
    assert messages_request1[3] == 'No body was attached to the request'
    assert messages_response1[0] == 'Response status: 202'
    assert messages_response1[1] == 'Response headers:'
    assert messages_request2[0] == "Request URL: 'http://localhost/'"
    assert messages_request2[1] == "Request method: 'GET'"
    assert messages_request2[2] == 'Request headers:'
    assert messages_request2[3] == 'No body was attached to the request'
    assert messages_response2[0] == 'Response status: 202'
    assert messages_response2[1] == 'Response headers:'

    mock_handler.reset()

    # Headers and query parameters

    policy.allowed_query_params = ['country']

    universal_request.headers = {
        "Accept": "Caramel",
        "Hate": "Chocolat",
    }
    http_response.headers = {
        "Content-Type": "Caramel",
        "HateToo": "Chocolat",
    }
    universal_request.url = "http://localhost/?country=france&city=aix"

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 2
    messages_request = mock_handler.messages[0].message.split("\n")
    messages_response = mock_handler.messages[1].message.split("\n")
    assert messages_request[0] == "Request URL: 'http://localhost/?country=france&city=REDACTED'"
    assert messages_request[1] == "Request method: 'GET'"
    assert messages_request[2] == "Request headers:"
    # Dict not ordered in Python, exact logging order doesn't matter
    assert set([
        messages_request[3],
        messages_request[4]
    ]) == set([
        "    'Accept': 'Caramel'",
        "    'Hate': 'REDACTED'"
    ])
    assert messages_request[5] == 'No body was attached to the request'
    assert messages_response[0] == "Response status: 202"
    assert messages_response[1] == "Response headers:"
    # Dict not ordered in Python, exact logging order doesn't matter
    assert set([
        messages_response[2],
        messages_response[3]
    ]) == set([
        "    'Content-Type': 'Caramel'",
        "    'HateToo': 'REDACTED'"
    ])

    mock_handler.reset()


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_http_logger_operation_level(http_request, http_response):

    class MockHandler(logging.Handler):
        def __init__(self):
            super(MockHandler, self).__init__()
            self.messages = []
        def reset(self):
            self.messages = []
        def emit(self, record):
            self.messages.append(record)
    mock_handler = MockHandler()

    logger = logging.getLogger("testlogger")
    logger.addHandler(mock_handler)
    logger.setLevel(logging.DEBUG)

    policy = HttpLoggingPolicy()
    kwargs={'logger': logger}

    universal_request = http_request('GET', 'http://localhost/')
    http_response = create_http_response(http_response, universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None, **kwargs))

    # Basics

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 2
    messages_request = mock_handler.messages[0].message.split("\n")
    messages_response = mock_handler.messages[1].message.split("\n")
    assert messages_request[0] == "Request URL: 'http://localhost/'"
    assert messages_request[1] == "Request method: 'GET'"
    assert messages_request[2] == 'Request headers:'
    assert messages_request[3] == 'No body was attached to the request'
    assert messages_response[0] == 'Response status: 202'
    assert messages_response[1] == 'Response headers:'

    mock_handler.reset()

    # Let's make this request a failure, retried twice

    request = PipelineRequest(universal_request, PipelineContext(None, **kwargs))

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 4
    messages_request1 = mock_handler.messages[0].message.split("\n")
    messages_response1 = mock_handler.messages[1].message.split("\n")
    messages_request2 = mock_handler.messages[2].message.split("\n")
    messages_response2 = mock_handler.messages[3].message.split("\n")
    assert messages_request1[0] == "Request URL: 'http://localhost/'"
    assert messages_request1[1] == "Request method: 'GET'"
    assert messages_request1[2] == 'Request headers:'
    assert messages_request1[3] == 'No body was attached to the request'
    assert messages_response1[0] == 'Response status: 202'
    assert messages_response1[1] == 'Response headers:'
    assert messages_request2[0] == "Request URL: 'http://localhost/'"
    assert messages_request2[1] == "Request method: 'GET'"
    assert messages_request2[2] == 'Request headers:'
    assert messages_request2[3] == 'No body was attached to the request'
    assert messages_response2[0] == 'Response status: 202'
    assert messages_response2[1] == 'Response headers:'

    mock_handler.reset()

@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_http_logger_with_body(http_request, http_response):

    class MockHandler(logging.Handler):
        def __init__(self):
            super(MockHandler, self).__init__()
            self.messages = []
        def reset(self):
            self.messages = []
        def emit(self, record):
            self.messages.append(record)
    mock_handler = MockHandler()

    logger = logging.getLogger("testlogger")
    logger.addHandler(mock_handler)
    logger.setLevel(logging.DEBUG)

    policy = HttpLoggingPolicy(logger=logger)

    universal_request = http_request('GET', 'http://localhost/')
    universal_request.body = "testbody"
    http_response = create_http_response(http_response, universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None))

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 2
    messages_request = mock_handler.messages[0].message.split("\n")
    messages_response = mock_handler.messages[1].message.split("\n")
    assert messages_request[0] == "Request URL: 'http://localhost/'"
    assert messages_request[1] == "Request method: 'GET'"
    assert messages_request[2] == 'Request headers:'
    assert messages_request[3] == 'A body is sent with the request'
    assert messages_response[0] == 'Response status: 202'
    assert messages_response[1] == 'Response headers:'

    mock_handler.reset()


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
@pytest.mark.skipif(sys.version_info < (3, 6), reason="types.AsyncGeneratorType does not exist in 3.5")
def test_http_logger_with_generator_body(http_request, http_response):

    class MockHandler(logging.Handler):
        def __init__(self):
            super(MockHandler, self).__init__()
            self.messages = []
        def reset(self):
            self.messages = []
        def emit(self, record):
            self.messages.append(record)
    mock_handler = MockHandler()

    logger = logging.getLogger("testlogger")
    logger.addHandler(mock_handler)
    logger.setLevel(logging.DEBUG)

    policy = HttpLoggingPolicy(logger=logger)

    universal_request = http_request('GET', 'http://localhost/')
    mock = Mock()
    mock.__class__ = types.AsyncGeneratorType
    universal_request.body = mock
    http_response = create_http_response(http_response, universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None))

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 2
    messages_request = mock_handler.messages[0].message.split("\n")
    messages_response = mock_handler.messages[1].message.split("\n")
    assert messages_request[0] == "Request URL: 'http://localhost/'"
    assert messages_request[1] == "Request method: 'GET'"
    assert messages_request[2] == 'Request headers:'
    assert messages_request[3] == 'File upload'
    assert messages_response[0] == 'Response status: 202'
    assert messages_response[1] == 'Response headers:'

    mock_handler.reset()
