# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import Any

from .client_assertion import ClientAssertionCredential


class TokenFileMixin(object):
    def __init__(
            self,
            token_file_path: str,
            **_
    ) -> None:
        super(TokenFileMixin, self).__init__()
        self._jwt = ""
        self._last_read_time = 0
        self._token_file_path = token_file_path

    def get_service_account_token(self) -> str:
        now = int(time.time())
        if now - self._last_read_time > 300:
            with open(self._token_file_path) as f:
                self._jwt = f.read()
            self._last_read_time = now
        return self._jwt


class TokenExchangeCredential(ClientAssertionCredential, TokenFileMixin):
    def __init__(
            self,
            tenant_id: str,
            client_id: str,
            token_file_path: str,
            **kwargs
    ) -> None:
        super(TokenExchangeCredential, self).__init__(
            tenant_id=tenant_id,
            client_id=client_id,
            func=self.get_service_account_token,
            token_file_path=token_file_path,
            **kwargs
        )
