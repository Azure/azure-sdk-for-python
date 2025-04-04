# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
from typing import Optional, Any

from azure.core.credentials import TokenCredential, AccessToken
from azure.identity import InteractiveBrowserCredential


class FabricTokenCredential(TokenCredential):

    def __init__(self):
        self.token_credential = InteractiveBrowserCredential()
        self.token_credential.authority = ''

    def get_token(self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None,
                  enable_cae: bool = False, **kwargs: Any) -> AccessToken:
        scopes = ["https://cosmos.azure.com/.default"]
        return self.token_credential.get_token(*scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae,
                                               **kwargs)
