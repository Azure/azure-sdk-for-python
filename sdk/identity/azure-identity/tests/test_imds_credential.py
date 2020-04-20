# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.transport import HttpResponse
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import CredentialUnavailableError
from azure.identity._credentials.managed_identity import ImdsCredential
import pytest

from helpers import mock, mock_response, Request, validating_transport


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


def test_identity_not_available():
    """The credential should raise CredentialUnavailableError when the endpoint responds 400 to a token request"""

    # first request is a probe, second a token request
    transport = validating_transport(
        requests=[Request()] * 2, responses=[mock_response(status_code=400, json_payload={})] * 2
    )

    credential = ImdsCredential(transport=transport)

    with pytest.raises(CredentialUnavailableError):
        credential.get_token("scope")


def test_unexpected_error():
    """The credential should raise ClientAuthenticationError when the endpoint returns an unexpected error"""

    error_message = "something went wrong"

    for code in range(401, 600):

        def send(request, **_):
            if "resource" not in request.query:
                # availability probe
                return mock_response(status_code=400, json_payload={})
            return mock_response(status_code=code, json_payload={"error": error_message})

        credential = ImdsCredential(transport=mock.Mock(send=send))

        with pytest.raises(ClientAuthenticationError) as ex:
            credential.get_token("scope")

        assert error_message in ex.value.message
