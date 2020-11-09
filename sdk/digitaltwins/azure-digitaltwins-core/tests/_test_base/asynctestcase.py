# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
import os

from azure.core.credentials import AccessToken

from devtools_testutils import AzureTestCase


class AsyncDigitalTwinsTestCase(AzureTestCase):

    class AsyncFakeCredential(object):
        # fake async credential
        async def get_token(self, *scopes, **kwargs):
            return AccessToken('fake_token', 2527537086)

        async def close(self):
            pass

    def create_basic_client(self, client_class, **kwargs):
        # This is the patch for creating client using aio identity

        tenant_id = os.environ.get("AZURE_TENANT_ID") or self.settings.ACTIVE_DIRECTORY_TENANT_ID
        client_id = os.environ.get("AZURE_CLIENT_ID") or self.settings.ACTIVE_DIRECTORY_APPLICATION_ID
        secret = os.environ.get("AZURE_CLIENT_SECRET") or self.settings.ACTIVE_DIRECTORY_APPLICATION_SECRET

        if tenant_id and client_id and secret and self.is_live:
            # Create azure-identity class using aio credential
            from azure.identity.aio import ClientSecretCredential
            credentials = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=secret
            )

        else:
            credentials = self.AsyncFakeCredential()

        kwargs.setdefault("logging_enable", True)
        client = client_class(
            credential=credentials,
            **kwargs
        )
        return client