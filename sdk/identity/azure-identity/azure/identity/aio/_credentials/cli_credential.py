# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import time
from datetime import datetime

import asyncio
from subprocess import Popen, PIPE

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError


class AzureCliCredential(object):

    _DEFAULT_PREFIX = "/.default"
    _CLI_NOT_INSTALLED_ERR = "Azure CLI not installed"
    _CLI_LOGIN_ERR = "ERROR: Please run 'az login' to setup account.\r\n"

    async def get_token(self, *scopes, **kwargs): # pylint:disable=unused-argument
        command = 'az account get-access-token'
        
        if scopes:
            resource = scopes[0]
            if resource.endswith(self._DEFAULT_PREFIX):
                resource = resource[:-len(self._DEFAULT_PREFIX)]

            command = ' '.join([command, '--resource', resource])

        try:
            get_access_token_stdout = await self._get_cli_access_token(command)
            get_access_token_object = json.loads(get_access_token_stdout)
            access_token = get_access_token_object['accessToken']
        except ClientAuthenticationError:
            raise
        except Exception as e:
            raise ClientAuthenticationError("Azure CLI didn't provide an access token")
        
        expires_on = int((
            datetime.strptime(get_access_token_object['expiresOn'], '%Y-%m-%d %H:%M:%S.%f')
                - datetime.now()
            ).total_seconds() + time.time())

        return AccessToken(access_token, expires_on)

    async def _get_cli_access_token(self, command):
        _proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            timeout=10)
            
        stdout, stderr = await _proc.communicate()

        if _proc.returncode == 127 or (_proc.returncode == 1 and 'not recognized as' in stderr):
            raise ClientAuthenticationError(self._CLI_NOT_INSTALLED_ERR)
        elif _proc.returncode == 1:
            raise ClientAuthenticationError(self._CLI_LOGIN_ERR)

        return stdout
