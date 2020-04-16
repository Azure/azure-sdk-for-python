# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.core.credentials import AccessToken
from azure.identity._credentials.win_vscode_credential import WinVSCodeCredential
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore
if sys.platform.startswith('win'):
    from azure.identity._credentials.win_vscode_credential import _read_credential, _cred_write

@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_win_vscode_credential():
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
    token_read = _read_credential(service_name, account_name)
    assert token_read == token_written

@pytest.mark.skipif(not sys.platform.startswith('win'), reason="This test only runs on Windows")
def test_get_token():
    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = Mock(return_value=expected_token)

    credential = WinVSCodeCredential(
        client=mock_client,
    )

    token = credential.get_token("scope")
    assert token is expected_token
    assert mock_client.obtain_token_by_refresh_token.call_count == 1
