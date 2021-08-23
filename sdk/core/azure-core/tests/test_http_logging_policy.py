# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the HttpLoggingPolicy."""

import logging
import types
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore
from azure.core.pipeline import (
    PipelineResponse,
    PipelineRequest,
    PipelineContext
)
from azure.core.pipeline.transport import (
    HttpRequest,
    HttpResponse,
)
from azure.core.pipeline.policies import (
    HttpLoggingPolicy,
)


def test_http_logger():

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

    universal_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_response = HttpResponse(universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None))

    # Basics

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 6
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'No body was attached to the request'
    assert mock_handler.messages[4].message == 'Response status: 202'
    assert mock_handler.messages[5].message == 'Response headers:'

    mock_handler.reset()

    # Let's make this request a failure, retried twice

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 12
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'No body was attached to the request'
    assert mock_handler.messages[4].message == 'Response status: 202'
    assert mock_handler.messages[5].message == 'Response headers:'
    assert mock_handler.messages[6].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[7].message == "Request method: 'GET'"
    assert mock_handler.messages[8].message == 'Request headers:'
    assert mock_handler.messages[9].message == 'No body was attached to the request'
    assert mock_handler.messages[10].message == 'Response status: 202'
    assert mock_handler.messages[11].message == 'Response headers:'

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
    universal_request.url = "http://127.0.0.1/?country=france&city=aix"

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 10
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/?country=france&city=REDACTED'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == "Request headers:"
    # Dict not ordered in Python, exact logging order doesn't matter
    assert set([
        mock_handler.messages[3].message,
        mock_handler.messages[4].message
    ]) == set([
        "    'Accept': 'Caramel'",
        "    'Hate': 'REDACTED'"
    ])
    assert mock_handler.messages[5].message == 'No body was attached to the request'
    assert mock_handler.messages[6].message == "Response status: 202"
    assert mock_handler.messages[7].message == "Response headers:"
    # Dict not ordered in Python, exact logging order doesn't matter
    assert set([
        mock_handler.messages[8].message,
        mock_handler.messages[9].message
    ]) == set([
        "    'Content-Type': 'Caramel'",
        "    'HateToo': 'REDACTED'"
    ])

    mock_handler.reset()



def test_http_logger_operation_level():

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

    universal_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_response = HttpResponse(universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None, **kwargs))

    # Basics

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 6
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'No body was attached to the request'
    assert mock_handler.messages[4].message == 'Response status: 202'
    assert mock_handler.messages[5].message == 'Response headers:'

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
    assert len(mock_handler.messages) == 12
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'No body was attached to the request'
    assert mock_handler.messages[4].message == 'Response status: 202'
    assert mock_handler.messages[5].message == 'Response headers:'
    assert mock_handler.messages[6].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[7].message == "Request method: 'GET'"
    assert mock_handler.messages[8].message == 'Request headers:'
    assert mock_handler.messages[9].message == 'No body was attached to the request'
    assert mock_handler.messages[10].message == 'Response status: 202'
    assert mock_handler.messages[11].message == 'Response headers:'

    mock_handler.reset()


def test_http_logger_with_body():

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

    universal_request = HttpRequest('GET', 'http://127.0.0.1/')
    universal_request.body = "testbody"
    http_response = HttpResponse(universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None))

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 6
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'A body is sent with the request'
    assert mock_handler.messages[4].message == 'Response status: 202'
    assert mock_handler.messages[5].message == 'Response headers:'

    mock_handler.reset()


def test_http_logger_with_generator_body():

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

    universal_request = HttpRequest('GET', 'http://127.0.0.1/')
    mock = Mock()
    mock.__class__ = types.GeneratorType
    universal_request.body = mock
    http_response = HttpResponse(universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None))

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 6
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'File upload'
    assert mock_handler.messages[4].message == 'Response status: 202'
    assert mock_handler.messages[5].message == 'Response headers:'

    mock_handler.reset()
