# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core import PipelineClient
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import (
    HttpRequest,
    RequestsTransport,
)
from azure.core.exceptions import IncompleteReadError
import pytest


@pytest.fixture(params=[True, False])
def stream(request):
    return request.param


def test_requests_transport_short_read_raises(port):
    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))
    with pytest.raises(IncompleteReadError):
        with Pipeline(RequestsTransport()) as pipeline:
            response = pipeline.run(request, stream=False)
            assert response.http_response.status_code == 200
            response.http_response.body()


def test_disable_content_length_checking_via_custom_hook(port):
    def hook(request, **kwargs):
        request.raw.enforce_content_length = False

    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))
    with Pipeline(RequestsTransport()) as pipeline:
        response = pipeline.run(request, hooks={"response": [hook]})
        assert response.http_response.status_code == 200
    # note the absence of a IncompleteRead exception


def test_user_hooks_merged(port):
    hook_called = [False]

    def hook(request, **kwargs):
        hook_called[0] = True

    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))
    with pytest.raises(IncompleteReadError):
        with Pipeline(RequestsTransport()) as pipeline:
            response = pipeline.run(request, hooks={"response": [hook]})
            assert response.http_response.status_code == 200
    assert hook_called[0]


def test_sync_transport_short_read_download_stream(port):
    url = "http://localhost:{}/errors/short-data".format(port)
    client = PipelineClient(url)
    request = HttpRequest("GET", url)
    with pytest.raises(IncompleteReadError):
        pipeline_response = client._pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.stream_download(client._pipeline)
        content = b""
        for d in data:
            content += d
