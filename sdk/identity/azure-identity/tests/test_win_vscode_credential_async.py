# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.core.credentials import AccessToken
from azure.identity.aio._credentials.win_vscode_credential import WinVSCodeCredential
from helpers_async import wrap_in_future
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
@pytest.mark.asyncio
async def test_get_token():
    client_id = "client id"
    tenant_id = "tenant"
    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    token_by_refresh_token = Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)

    credential = WinVSCodeCredential(
        client_id=client_id,
        tenant_id=tenant_id,
        client=mock_client,
    )

    token = await credential.get_token("scope")
    assert token is expected_token
