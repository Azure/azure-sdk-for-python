# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .client_assertion import ClientAssertionCredential
from ..._credentials.token_exchange import TokenFileMixin


class TokenExchangeCredential(ClientAssertionCredential, TokenFileMixin):
    def __init__(self, tenant_id: str, client_id: str, token_file_path: str, **kwargs) -> None:
        super().__init__(
            tenant_id=tenant_id,
            client_id=client_id,
            func=self.get_service_account_token,
            token_file_path=token_file_path,
            **kwargs
        )
