# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
_IS_PY2 = sys.version_info[0] < 3

import platform
_PLATFORM_STR = platform.system()
_PLATFORM = 1 if _PLATFORM_STR == 'Windows' else 2 if _PLATFORM_STR == 'Linux' else 3
_USE_SHELL = True if _PLATFORM == 1 else False

import json
import time
from datetime import datetime

from subprocess import check_output, check_call, CalledProcessError, STDOUT, PIPE
try:
    from subprocess import run
except:
    pass

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

        if _IS_PY2:
            try:
                get_access_token_stdout = check_output(command, shell=_USE_SHELL, stderr=STDOUT)
                get_access_token_stderr = ''
            except CalledProcessError as e:
                if self._WINDOWS_CMD_NOT_FOUND in e.output or self._LINUX_CMD_NOT_FOUND in e.output:
                    raise BaseException(self._CLI_NOT_INSTALLED_ERR)
                else:
                    raise ClientAuthenticationError(e.output)
            except:
                raise BaseException(self._CLI_NOT_INSTALLED_ERR) # azure cli not installed for mac os
        else:
            try:
                get_access_token = run(command, shell=_USE_SHELL, stdout=PIPE, stderr=PIPE)
            except:
                raise BaseException(self._CLI_NOT_INSTALLED_ERR) # azure cli not installed for mac os
            get_access_token_stdout = get_access_token.stdout.decode("utf-8")
            get_access_token_stderr = get_access_token.stderr.decode("utf-8")

            if get_access_token_stderr or not get_access_token_stdout:
                if self._LINUX_CMD_NOT_FOUND in get_access_token_stderr\
                    or self._WINDOWS_CMD_NOT_FOUND in get_access_token_stderr:
                    raise BaseException(self._CLI_NOT_INSTALLED_ERR)
                else:
                    raise ClientAuthenticationError(message=get_access_token_stderr)

        get_access_token_object = json.loads(get_access_token_stdout)
        access_token = get_access_token_object['accessToken']
        expires_on = int((
            datetime.strptime(
                self.__microseconds_parsed(get_access_token_object['expiresOn']), '%Y-%m-%d %H:%M:%S.%f').utcnow()
                - datetime.now()
            ).total_seconds() + time.time())

        return AccessToken(access_token, expires_on)

    @classmethod
    def __microseconds_parsed(cls, timestamp):
        _index = timestamp.index('.')
        _microseconds = timestamp[_index + 1:]
        return '.'.join([timestamp[:_index]] + ['{:06d}'.format(int(_microseconds))])
