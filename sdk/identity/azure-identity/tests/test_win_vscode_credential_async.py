# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.core.credentials import AccessToken
from helpers_async import wrap_in_future
from unittest.mock import Mock
if sys.platform.startswith('win'):
    from azure.identity.aio._credentials.win_vscode_credential import WinVSCodeCredential
    from azure.identity._credentials.win_vscode_credential import _cred_write

@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
@pytest.mark.asyncio
async def test_get_token():
    service_name = u"VS Code Azure"
    account_name = u"Azure"
    target = u"{}/{}".format(service_name, account_name)
    comment = u"comment"
    token_written = u"test_refresh_token"
    user_name = u"Azure"
    credential = {"Type": 0x1,
                  "TargetName": target,
                  "UserName": user_name,
                  "CredentialBlob": token_written,
                  "Comment": comment,
                  "Persist": 0x2}
    _cred_write(credential)

    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    token_by_refresh_token = Mock(return_value=expected_token)
    mock_client.obtain_token_by_refresh_token = wrap_in_future(token_by_refresh_token)

    credential = WinVSCodeCredential(
        _client=mock_client,
    )

    token = await credential.get_token("scope")
    assert token is expected_token
