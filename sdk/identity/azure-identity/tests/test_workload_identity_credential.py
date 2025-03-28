# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import mock_open, MagicMock, patch
from urllib.parse import urlparse

import pytest
from azure.identity import WorkloadIdentityCredential
from azure.identity._internal.aad_client_base import JWT_BEARER_ASSERTION

from helpers import mock_response, build_aad_response, get_discovery_response, GET_TOKEN_METHODS


def test_workload_identity_credential_initialize():
    tenant_id = "tenant-id"
    client_id = "client-id"

    credential: WorkloadIdentityCredential = WorkloadIdentityCredential(
        tenant_id=tenant_id, client_id=client_id, token_file_path="foo-path"
    )


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_workload_identity_credential_get_token(get_token_method):
    tenant_id = "tenant-id"
    client_id = "client-id"
    access_token = "foo"
    token_file_path = "foo-path"
    assertion = "foo-assertion"
    scope = "scope"

    def send(request, **kwargs):
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert request.data.get("client_assertion") == assertion
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))

        assert request.data["client_assertion"] == assertion
        assert request.data["client_assertion_type"] == JWT_BEARER_ASSERTION
        assert request.data["client_id"] == client_id
        assert request.data["grant_type"] == "client_credentials"
        assert request.data["scope"] == scope
        assert tenant_id in request.url
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    transport = MagicMock(send=send)
    credential: WorkloadIdentityCredential = WorkloadIdentityCredential(
        tenant_id=tenant_id, client_id=client_id, token_file_path=token_file_path, transport=transport
    )

    open_mock = mock_open(read_data=assertion)
    with patch("builtins.open", open_mock):
        token = getattr(credential, get_token_method)(scope)
        assert token.token == access_token

    open_mock.assert_called_once_with(token_file_path, encoding="utf-8")
