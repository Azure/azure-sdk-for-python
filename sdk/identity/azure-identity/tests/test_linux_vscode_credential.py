# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import pytest
from azure.core.credentials import AccessToken
try:
    from azure.identity._credentials.linux_vscode_credential import LinuxVSCodeCredential
except (ImportError, OSError):
    pass
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore


@pytest.mark.skipif(sys.platform.startswith('darwin') or sys.platform.startswith('win'), reason="This test only runs on Linux")
def test_get_token():
    expected_token = AccessToken("token", 42)

    mock_client = Mock(spec=object)
    mock_client.obtain_token_by_refresh_token = Mock(return_value=expected_token)

    credential = LinuxVSCodeCredential(
        client=mock_client,
    )

    token = credential.get_token("scope")
    assert token is expected_token
    assert mock_client.obtain_token_by_refresh_token.call_count == 1
