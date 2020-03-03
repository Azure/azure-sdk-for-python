# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .._credentials.base import AsyncCredentialBase
from ..._credentials import AzureCliCredential as _SyncAzureCliCredential


class AzureCliCredential(AsyncCredentialBase):
    """Authenticates by requesting a token from the Azure CLI.

    This requires previously logging in to Azure via "az login", and will use the CLI's currently logged in identity.
    """

    async def get_token(self, *scopes, **kwargs):
        """Request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        Only one scope is supported per request. This credential won't cache tokens. Every call invokes the Azure CLI.

        :param str scopes: desired scopes for the token. Only **one** scope is supported per call.
        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke the Azure CLI.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked the Azure CLI but didn't
          receive an access token.
        """
        return _SyncAzureCliCredential().get_token(*scopes, **kwargs)

    async def close(self):
        return
