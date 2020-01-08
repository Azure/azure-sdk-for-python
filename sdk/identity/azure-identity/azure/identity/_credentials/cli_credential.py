# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import platform
_USE_SHELL = platform.system() == 'Windows'

import json
import time
from datetime import datetime

from subprocess import check_output, CalledProcessError, STDOUT
import six

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError


def _microseconds_parsed(timestamp):
    _index = timestamp.index('.')
    _microseconds = timestamp[_index + 1:]
    return '.'.join([timestamp[:_index]] + ['{:06d}'.format(int(_microseconds))])


class CliCredential(object):

    _LINUX_CMD_NOT_FOUND = 'command not found'
    _WINDOWS_CMD_NOT_FOUND = 'is not recognized as'
    _DEFAULT_PREFIX = "/.default"
    _CLI_NOT_INSTALLED_ERR = "Azure CLI not installed"

    def get_token(self, *scopes, **kwargs): # pylint:disable=unused-argument
        command = ['az', 'account', 'get-access-token']

        if scopes:
            resource = scopes[0]
            if resource.endswith(self._DEFAULT_PREFIX):
                resource = resource[:-len(self._DEFAULT_PREFIX)]

            command.extend(['--resource', resource])

        get_access_token_stdout = self._get_proc_stdout(command)
        get_access_token_object = json.loads(get_access_token_stdout)
        access_token = get_access_token_object['accessToken']
        expires_on = int((
            datetime.strptime(
                _microseconds_parsed(get_access_token_object['expiresOn']), '%Y-%m-%d %H:%M:%S.%f')
                - datetime.now()
            ).total_seconds() + time.time())

        return AccessToken(access_token, expires_on)

    def _get_proc_stdout(self, command):
        try:
            _stdout = check_output(command, shell=_USE_SHELL, stderr=STDOUT)
        except CalledProcessError as e:
            _stderr = six.ensure_str(e.output)
            if self._WINDOWS_CMD_NOT_FOUND in _stderr or self._LINUX_CMD_NOT_FOUND in _stderr:
                raise ClientAuthenticationError(self._CLI_NOT_INSTALLED_ERR)
            else:
                raise ClientAuthenticationError(_stderr)
        except:
            raise ClientAuthenticationError(self._CLI_NOT_INSTALLED_ERR) # azure cli not installed in mac os
        else:
            return _stdout
