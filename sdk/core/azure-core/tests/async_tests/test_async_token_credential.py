# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest


@pytest.mark.asyncio
async def async_token_credential_inheritance():
    from azure.core.credentials_async import AsyncTokenCredential

    class TestTokenCredential(AsyncTokenCredential):
        async def get_token(self, *scopes, **kwargs):
            return "TOKEN"

    cred = TestTokenCredential()
    await cred.get_token("scope")
