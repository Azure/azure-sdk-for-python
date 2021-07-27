# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from typing import TYPE_CHECKING

from .client_assertion import ClientAssertionCredential
from .._constants import EnvironmentVariables

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import AccessToken


class TokenFileMixin(object):
    def __init__(self):
        # type: () -> None
        super(TokenFileMixin, self).__init__()
        self._jwt = ""
        self._last_read_time = 0
        self._token_file_path = os.environ[EnvironmentVariables.TOKEN_FILE_PATH]

    def get_service_account_token(self):
        # type: () -> str
        now = int(time.time())
        if now - self._last_read_time > 300:
            with open(self._token_file_path) as f:
                self._jwt = f.read()
            self._last_read_time = now
        return self._jwt


class TokenExchangeCredential(TokenFileMixin):
    def __init__(self, **kwargs):
        # type: (**Any) -> None
        super(TokenExchangeCredential, self).__init__()
        self._credential = ClientAssertionCredential(
            os.environ[EnvironmentVariables.AZURE_TENANT_ID],
            os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
            self.get_service_account_token,
            **kwargs
        )

    def __enter__(self):
        self._credential.__enter__()
        return self

    def __exit__(self, *args):
        self._credential.__exit__(*args)

    def close(self):
        # type: () -> None
        self.__exit__()

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        return self._credential.get_token(*scopes, **kwargs)
