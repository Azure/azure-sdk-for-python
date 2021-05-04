# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.credentials import AccessToken
from devtools_testutils import AzureTestCase

from azure.mixedreality.authentication._shared.aio.static_access_token_credential import StaticAccessTokenCredential

class TestAsyncStaticAccessTokenCredential:
    @AzureTestCase.await_prepared_test
    async def test_get_token(self):
        token = "My access token"
        expiration = 0

        access_token = AccessToken(token=token, expires_on=expiration)
        staticAccessToken = StaticAccessTokenCredential(access_token)

        actual = await staticAccessToken.get_token()

        assert access_token == actual
