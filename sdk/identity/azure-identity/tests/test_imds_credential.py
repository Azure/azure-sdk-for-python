# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.transport import HttpResponse
from azure.core.exceptions import HttpResponseError
from azure.identity._credentials.managed_identity import ImdsCredential
import pytest

from helpers import mock, mock_response


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    successful_probe = mock_response(status_code=400, json_payload={})
    transport = mock.Mock(send=mock.Mock(return_value=successful_probe))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        credential.get_token()


def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    successful_probe = mock_response(status_code=400, json_payload={})
    transport = mock.Mock(send=mock.Mock(return_value=successful_probe))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        credential.get_token("one scope", "and another")
