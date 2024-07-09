# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import functools
import os
from typing import Any, Optional

from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpRequest

from .._internal import AsyncContextManager
from .._internal.managed_identity_base import AsyncManagedIdentityBase
from .._internal.managed_identity_client import AsyncManagedIdentityClient


class AzureMLOnBehalfOfCredential(AsyncContextManager):
    # pylint: disable=line-too-long
    """Authenticates a user via the on-behalf-of flow.

    This credential can only be used on `Azure Machine Learning Compute.
    <https://docs.microsoft.com/azure/machine-learning/concept-compute-target#azure-machine-learning-compute-managed>`_ during job execution when user request to
    run job during its identity.
    """
    # pylint: enable=line-too-long

    def __init__(self, **kwargs: Any):
        self._credential = _AzureMLOnBehalfOfCredential(**kwargs)

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param scopes: The desired scope for the access token. This credential allows only one scope per request.
        :type scopes: str
        :rtype: ~azure.core.credentials.AccessToken
        :return: The access token for temporary access token for the requested scope.
        :raises: ~azure.ai.ml.identity.CredentialUnavailableError
        """

        return await self._credential.get_token(*scopes, **kwargs)

    async def __aenter__(self) -> "AzureMLOnBehalfOfCredential":
        if self._credential:
            await self._credential.__aenter__()
        return self

    async def close(self) -> None:
        """Close the credential's transport session."""
        if self._credential:
            await self._credential.__aexit__()


class _AzureMLOnBehalfOfCredential(AsyncManagedIdentityBase):
    def get_client(self, **kwargs):
        # type: (**Any) -> Optional[AsyncManagedIdentityClient]
        client_args = _get_client_args(**kwargs)
        if client_args:
            return AsyncManagedIdentityClient(**client_args)
        return None

    def get_unavailable_message(self):
        # type: () -> str
        return "AzureML On Behalf of credentials not available in this environment"


def _get_client_args(**kwargs):
    # type: (dict) -> Optional[dict]

    url = os.environ.get("OBO_ENDPOINT")
    if not url:
        # OBO identity isn't available in this environment
        return None

    return dict(
        kwargs,
        request_factory=functools.partial(_get_request, url),
    )


def _get_request(url, resource):
    # type: (str, str) -> HttpRequest
    request = HttpRequest("GET", url)
    request.format_parameters(dict({"resource": resource}))
    return request
