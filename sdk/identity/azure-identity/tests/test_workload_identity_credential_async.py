# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import mock_open, patch, MagicMock

import pytest
from azure.identity.aio import WorkloadIdentityCredential

from helpers import mock_response, build_aad_response, GET_TOKEN_METHODS


def test_workload_identity_credential_initialize():
    tenant_id = "tenant-id"
    client_id = "client-id"

    credential: WorkloadIdentityCredential = WorkloadIdentityCredential(
        tenant_id=tenant_id, client_id=client_id, token_file_path="foo-path"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_workload_identity_credential_get_token(get_token_method):
    tenant_id = "tenant-id"
    client_id = "client-id"
    access_token = "foo"
    token_file_path = "foo-path"
    assertion = "foo-assertion"

    async def send(request, **kwargs):
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert request.data.get("client_assertion") == assertion
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    transport = MagicMock(send=send)
    credential: WorkloadIdentityCredential = WorkloadIdentityCredential(
        tenant_id=tenant_id, client_id=client_id, token_file_path=token_file_path, transport=transport
    )

    open_mock = mock_open(read_data=assertion)
    with patch("builtins.open", open_mock):
        token = await getattr(credential, get_token_method)("scope")
        assert token.token == access_token

    open_mock.assert_called_once_with(token_file_path, encoding="utf-8")
