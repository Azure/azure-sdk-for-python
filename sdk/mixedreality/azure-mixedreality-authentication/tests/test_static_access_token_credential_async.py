# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.core.credentials import AccessToken

from azure.mixedreality.authentication._shared.aio.static_access_token_credential import StaticAccessTokenCredential

class TestAsyncStaticAccessTokenCredential:

    @pytest.mark.asyncio
    async def test_get_token(self):
        token = "My access token"
        expiration = 0

        access_token = AccessToken(token=token, expires_on=expiration)
        static_access_token = StaticAccessTokenCredential(access_token)

        actual = await static_access_token.get_token()

        assert access_token == actual
