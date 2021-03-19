# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ServiceRequestError
from azure.identity._internal.msal_client import MsalClient

import pytest

from helpers import mock


def test_retries_requests():
    """The client should retry token requests"""

    message = "can't connect"
    transport = mock.Mock(send=mock.Mock(side_effect=ServiceRequestError(message)))
    client = MsalClient(transport=transport)

    with pytest.raises(ServiceRequestError, match=message):
        client.post("https://localhost")
    assert transport.send.call_count > 1
    transport.send.reset_mock()

    with pytest.raises(ServiceRequestError, match=message):
        client.get("https://localhost")
    assert transport.send.call_count > 1
