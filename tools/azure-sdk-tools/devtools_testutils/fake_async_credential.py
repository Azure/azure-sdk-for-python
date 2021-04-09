# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
class AsyncFakeCredential(object):
    async def get_token(self, *scopes, **kwargs):
        from azure.core.credentials import AccessToken

        return AccessToken("fake_token", 2527537086)

    async def close(self):
        pass
