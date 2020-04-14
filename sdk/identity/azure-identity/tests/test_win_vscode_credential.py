# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.identity._credentials.win_vscode_credential import _read_credential
import win32cred

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
    win32cred.CredWrite(credential)
    token_read = _read_credential(service_name, account_name)
    assert token_read == token_written