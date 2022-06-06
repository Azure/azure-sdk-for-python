# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

from .client_assertion import ClientAssertionCredential

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any


class TokenFileMixin(object):
    def __init__(self, token_file_path, **_):
        # type: (str, **Any) -> None
        super(TokenFileMixin, self).__init__()
        self._jwt = ""
        self._last_read_time = 0
        self._token_file_path = token_file_path

    def get_service_account_token(self):
        # type: () -> str
        now = int(time.time())
        if now - self._last_read_time > 300:
            with open(self._token_file_path) as f:
                self._jwt = f.read()
            self._last_read_time = now
        return self._jwt


class TokenExchangeCredential(ClientAssertionCredential, TokenFileMixin):
    def __init__(self, tenant_id, client_id, token_file_path, **kwargs):
        # type: (str, str, str, **Any) -> None
        super(TokenExchangeCredential, self).__init__(
            tenant_id=tenant_id,
            client_id=client_id,
            func=self.get_service_account_token,
            token_file_path=token_file_path,
            **kwargs
        )
