# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.rest import HttpRequest
from corehttp.transport.requests import RequestsTransport

"""This file does a simple call to the testserver to make sure we can use the testserver"""


def test_smoke(port):
    request = HttpRequest(method="GET", url="http://localhost:{}/basic/string".format(port))
    with RequestsTransport() as sender:
        response = sender.send(request)
        response.raise_for_status()
        assert response.text() == "Hello, world!"
