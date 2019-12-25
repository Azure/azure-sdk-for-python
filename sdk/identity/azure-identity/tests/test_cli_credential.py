# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
_IS_PY2 = sys.version_info[0] == 2
import json

from azure.identity import CliCredential
from azure.core.exceptions import ClientAuthenticationError

from unittest.mock import Mock, patch


def test_cli_credential():
    access_token = '***'
    expires_on = '9999-1-1 00:00:00.1' 

    cred = CliCredential()
    cred._get_proc_stdout = Mock(return_value=json.dumps({"accessToken" : access_token, "expiresOn" : expires_on}))
    token = cred.get_token()
    assert token.token == access_token

def test_cli_installation():
    cred = CliCredential()
    try:
        token = cred.get_token()
    except ClientAuthenticationError:
        pass
    except Exception as e:
        assert CliCredential._CLI_NOT_INSTALLED_ERR in repr(e)

def test_cli_login():
    cred = CliCredential()
    try:
        token = cred.get_token()
    except ClientAuthenticationError as e:
        assert 'az login' in repr(e)
