# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import platform
_IS_WINDOWS = platform.system() == 'Windows'

import json
import time
from datetime import datetime

from subprocess import run, PIPE
import six

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError


def _microseconds_parsed(timestamp):
    _index = timestamp.index('.')
    _microseconds = timestamp[_index + 1:]
    return '.'.join([timestamp[:_index]] + ['{:06d}'.format(int(_microseconds))])


class AzureCliCredential(object):

    _DEFAULT_PREFIX = "/.default"
    _CLI_NOT_INSTALLED_ERR = "Azure CLI not installed"
    _CLI_LOGIN_ERR = "ERROR: Please run 'az login' to setup account.\r\n"

    def get_token(self, *scopes, **kwargs): # pylint:disable=unused-argument
        command = ['az', 'account', 'get-access-token']
        command2 = 'az account get-access-token'
        
        if scopes:
            resource = scopes[0]
            if resource.endswith(self._DEFAULT_PREFIX):
                resource = resource[:-len(self._DEFAULT_PREFIX)]

            command.extend(['--resource', resource])
            command2 = ' '.join([command2, '--resource', resource])

        get_access_token_stdout = self._get_cli_access_token(command if _IS_WINDOWS else command2)
        get_access_token_object = json.loads(get_access_token_stdout)
        access_token = get_access_token_object['accessToken']
        expires_on = int((
            datetime.strptime(
                _microseconds_parsed(get_access_token_object['expiresOn']), '%Y-%m-%d %H:%M:%S.%f')
                - datetime.now()
            ).total_seconds() + time.time())

        return AccessToken(access_token, expires_on)

    def _get_cli_access_token(self, command):
        _proc = run(command, shell=True, stderr=PIPE, stdout=PIPE)
        return_code = _proc.returncode
        stdout = six.ensure_str(_proc.stdout)
        stderr = six.ensure_str(_proc.stderr)
        if return_code == 127 or (return_code == 1 and 'not recognized as' in stderr):
            raise ClientAuthenticationError(self._CLI_NOT_INSTALLED_ERR)
        elif return_code == 1:
            raise ClientAuthenticationError(self._CLI_LOGIN_ERR)
        # elif : need to handle other/unexcepted error?
        
        return stdout
