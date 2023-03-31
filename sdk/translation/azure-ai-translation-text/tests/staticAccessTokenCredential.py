# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.credentials import TokenCredential, AccessToken
from typing import Optional

class StaticAccessTokenCredential (TokenCredential):
    token = ""
    def __init__(self, token=AccessToken):
        if token is AccessToken:
            self.token = token
    
    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs
    ) -> AccessToken:
        return self.token