# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.transport.requests import RequestsTransport
from utils import HTTP_REQUESTS

"""This file does a simple call to the testserver to make sure we can use the testserver"""


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_smoke(port, http_request):
    request = http_request(method="GET", url="http://localhost:{}/basic/string".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request)
        response.raise_for_status()
        assert response.text() == "Hello, world!"
