# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
_IS_PY2 = sys.version_info[0] == 2

import platform
_PLATFORM_STR = platform.system()
_PLATFORM = 1 if _PLATFORM_STR == 'Windows' else 2 if _PLATFORM_STR == 'Linux' else 3
_USE_SHELL = True if _PLATFORM == 1 else False

import json
import time
from datetime import datetime

from subprocess import check_output, CalledProcessError, STDOUT

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

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

        try:
            get_access_token_stdout = check_output(command, shell=_USE_SHELL, stderr=STDOUT)
        except CalledProcessError as e:
            e_msg = e.output if _IS_PY2 else e.output.decode('utf-8')
            if self._WINDOWS_CMD_NOT_FOUND in e_msg or self._LINUX_CMD_NOT_FOUND in e_msg:
                raise BaseException(self._CLI_NOT_INSTALLED_ERR)
            else:
                raise ClientAuthenticationError(e_msg)
        except:
            raise BaseException(self._CLI_NOT_INSTALLED_ERR) # azure cli not installed in mac os

        get_access_token_object = json.loads(get_access_token_stdout)
        access_token = get_access_token_object['accessToken']
        expires_on = int((
            datetime.strptime(
                self.__microseconds_parsed(get_access_token_object['expiresOn']), '%Y-%m-%d %H:%M:%S.%f')
                - datetime.now()
            ).total_seconds() + time.time())

        return AccessToken(access_token, expires_on)

    @classmethod
    def __microseconds_parsed(cls, timestamp):
        _index = timestamp.index('.')
        _microseconds = timestamp[_index + 1:]
        return '.'.join([timestamp[:_index]] + ['{:06d}'.format(int(_microseconds))])
