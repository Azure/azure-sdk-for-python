# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Union, Optional, cast, overload

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline import PipelineResponse, PipelineRequest
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy

from .._constants import STORAGE_OAUTH_SCOPE
from .._authentication import _HttpChallenge, AzureSasCredentialPolicy, SharedKeyCredentialPolicy


class AsyncBearerTokenChallengePolicy(AsyncBearerTokenCredentialPolicy):
    """Adds a bearer token Authorization header to requests, for the tenant provided in authentication challenges.

    See https://docs.microsoft.com/azure/active-directory/develop/claims-challenge for documentation on AAD
    authentication challenges.

    :param credential: The credential.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param str scopes: Lets you specify the type of access needed.
    :keyword bool discover_tenant: Determines if tenant discovery should be enabled. Defaults to True.
    :keyword bool discover_scopes: Determines if scopes from authentication challenges should be provided to token
        requests, instead of the scopes given to the policy's constructor, if any are present. Defaults to True.
    """

    def __init__(
        self,
        credential: AsyncTokenCredential,
        *scopes: str,
        discover_tenant: bool = True,
        discover_scopes: bool = True,
        **kwargs,
    ) -> None:
        self._discover_tenant = discover_tenant
        self._discover_scopes = discover_scopes
        super().__init__(credential, *scopes, **kwargs)

    async def on_challenge(self, request: PipelineRequest, response: PipelineResponse) -> bool:
        """Authorize request according to an authentication challenge

        This method is called when the resource provider responds 401 with a WWW-Authenticate header.

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :returns: a bool indicating whether the policy should send the request
        :rtype: bool
        """
        if not self._discover_tenant and not self._discover_scopes:
            # We can't discover the tenant or use a different scope; the request will fail because it hasn't changed
            return False

        try:
            challenge = _HttpChallenge(response.http_response.headers.get("WWW-Authenticate"))
            # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
            # if no scopes are included in the challenge, challenge.scope and challenge.resource will both be ''
            scope = challenge.scope or challenge.resource + "/.default" if self._discover_scopes else self._scopes
            if scope == "/.default":
                scope = self._scopes
        except ValueError:
            return False

        if self._discover_tenant:
            await self.authorize_request(request, scope, tenant_id=challenge.tenant_id)
        else:
            await self.authorize_request(request, scope)
        return True


@overload
def _configure_credential(credential: AzureNamedKeyCredential) -> SharedKeyCredentialPolicy:
    ...


@overload
def _configure_credential(credential: SharedKeyCredentialPolicy) -> SharedKeyCredentialPolicy:
    ...


@overload
def _configure_credential(credential: AzureSasCredential) -> AzureSasCredentialPolicy:
    ...


@overload
def _configure_credential(credential: AsyncTokenCredential) -> AsyncBearerTokenChallengePolicy:
    ...


@overload
def _configure_credential(credential: None) -> None:
    ...


def _configure_credential(
    credential: Optional[
        Union[AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential, SharedKeyCredentialPolicy]
    ]
) -> Optional[Union[AsyncBearerTokenChallengePolicy, AzureSasCredentialPolicy, SharedKeyCredentialPolicy]]:
    if hasattr(credential, "get_token"):
        credential = cast(AsyncTokenCredential, credential)
        return AsyncBearerTokenChallengePolicy(credential, STORAGE_OAUTH_SCOPE)
    if isinstance(credential, SharedKeyCredentialPolicy):
        return credential
    if isinstance(credential, AzureSasCredential):
        return AzureSasCredentialPolicy(credential)
    if isinstance(credential, AzureNamedKeyCredential):
        return SharedKeyCredentialPolicy(credential)
    if credential is not None:
        raise TypeError(f"Unsupported credential: {type(credential)}")
    return None
