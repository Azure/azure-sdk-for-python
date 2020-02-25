# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import time
from datetime import datetime

from subprocess import run, PIPE
import six

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError


class AzureCliCredential(object):

    _DEFAULT_PREFIX = "/.default"
    _CLI_NOT_INSTALLED_ERR = "Azure CLI not installed"
    _CLI_LOGIN_ERR = "ERROR: Please run 'az login' to setup account.\r\n"

    def get_token(self, *scopes, **kwargs): # pylint:disable=unused-argument
        command = 'az account get-access-token'
        
        if scopes:
            resource = scopes[0]
            if resource.endswith(self._DEFAULT_PREFIX):
                resource = resource[:-len(self._DEFAULT_PREFIX)]

            command = ' '.join([command, '--resource', resource])

        try:
            get_access_token_stdout = self._get_cli_access_token(command)
            get_access_token_object = json.loads(get_access_token_stdout)
            access_token = get_access_token_object['accessToken']
        except ClientAuthenticationError:
            raise
        except Exception as e:
            raise ClientAuthenticationError(repr(e))
        
        expires_on = int((
            datetime.strptime(get_access_token_object['expiresOn'], '%Y-%m-%d %H:%M:%S.%f')
                - datetime.now()
            ).total_seconds() + time.time())

        return AccessToken(access_token, expires_on)

    def _get_cli_access_token(self, command):
        _proc = run(command, shell=True, stderr=PIPE, stdout=PIPE, timeout=10)
        return_code = _proc.returncode
        stdout = six.ensure_str(_proc.stdout)
        stderr = six.ensure_str(_proc.stderr)
        if return_code == 127 or (return_code == 1 and 'not recognized as' in stderr):
            raise ClientAuthenticationError(self._CLI_NOT_INSTALLED_ERR)
        elif return_code == 1:
            raise ClientAuthenticationError(self._CLI_LOGIN_ERR)
        
        return stdout
