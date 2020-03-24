# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import HttpResponseError
from azure.identity._credentials.managed_identity import ImdsCredential
import pytest

from helpers import mock


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    # the credential will probe the endpoint, taking HttpResponseError as indicating availability
    transport = mock.Mock(send=mock.Mock(side_effect=HttpResponseError()))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        credential.get_token()


def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    # the credential will probe the endpoint, taking HttpResponseError as indicating availability
    transport = mock.Mock(send=mock.Mock(side_effect=HttpResponseError()))
    credential = ImdsCredential(transport=transport)

    with pytest.raises(ValueError):
        credential.get_token("one scope", "and another")
