# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from datetime import datetime
from subprocess import run, PIPE, CalledProcessError

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

class CliCredential(object):

    _DEFAULT_PREFIX = "/.default"
    _CLI_NOT_INSTALLED_ERR = "Azure CLI not installed"

    def get_token(self, *scopes, **kwargs): # pylint:disable=unused-argument
        command = ['az', 'account', 'get-access-token']

        if scopes:
            resource = scopes[0]
            if resource.endswith(self._DEFAULT_PREFIX):
                resource = resource[:-len(self._DEFAULT_PREFIX)]

            command.extend(['--resource', resource])

        self.__check_cli_installed()

        get_access_token = run(command, shell=True, stdout=PIPE, stderr=PIPE)

        get_access_token_stdout = get_access_token.stdout.decode("utf-8")
        get_access_token_stderr = get_access_token.stderr.decode("utf-8")

        if get_access_token_stderr or not get_access_token_stdout:
            raise ClientAuthenticationError(message=get_access_token_stderr)

        get_access_token_object = json.loads(get_access_token_stdout)
        access_token = get_access_token_object['accessToken']
        expires_on = int((
            datetime.strptime(
                self.__microseconds_parsed(get_access_token_object['expiresOn']), '%Y-%m-%d %H:%M:%S.%f').utcnow()
                - datetime(1970, 1, 1)
            ).total_seconds())

        return AccessToken(access_token, expires_on)

    @classmethod
    def __check_cli_installed(cls):
        try:
            run(['az'], shell=True, check=True)
        except CalledProcessError as e:
            raise ClientAuthenticationError(message=cls._CLI_NOT_INSTALLED_ERR)

    @classmethod
    def __microseconds_parsed(cls, timestamp):
        _index = timestamp.index('.')
        _microseconds = timestamp[_index + 1:]
        return '.'.join([timestamp[:_index]] + ['{:06d}'.format(int(_microseconds))])
