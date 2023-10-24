# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from corehttp.runtime import PipelineClient
from corehttp.rest import HttpRequest
from corehttp.exceptions import IncompleteReadError
import pytest


def test_sync_transport_short_read_download_stream(port):
    url = "http://localhost:{}/errors/short-data".format(port)
    client = PipelineClient(url)
    request = HttpRequest("GET", url)
    with pytest.raises(IncompleteReadError):
        pipeline_response = client.pipeline.run(request, stream=True)
        response = pipeline_response.http_response
        data = response.iter_bytes()
        content = b""
        for d in data:
            content += d
