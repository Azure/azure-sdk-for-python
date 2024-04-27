# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore teamprojectid, planid, jobid, oidctoken
from typing import Any, Optional

from azure.core.exceptions import ClientAuthenticationError
from azure.core.credentials import AccessToken
from azure.core.rest import HttpResponse

from .client_assertion import ClientAssertionCredential
from ..._credentials.azure_pipelines import build_oidc_request, validate_env_vars
from .._internal import AsyncContextManager
from ..._internal import validate_tenant_id
from ..._internal.pipeline import build_pipeline


class AzurePipelinesCredential(AsyncContextManager):
    """Authenticates using Microsoft Entra Workload ID in Azure Pipelines.

    This credential enable authentication in Azure Pipelines using workload identity federation for Azure service
    connections.

    :keyword str service_connection_id: The service connection ID, as found in the querystring's resourceId key.
        Required.
    :keyword str tenant_id: ID of the application's Microsoft Entra tenant. Also called its "directory" ID.
    :keyword str client_id: The client ID of a Microsoft Entra app registration.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_azure_pipelines_credential_async]
            :end-before: [END create_azure_pipelines_credential_async]
            :language: python
            :dedent: 4
            :caption: Create an AzurePipelinesCredential.
    """

    def __init__(
        self,
        *,
        tenant_id: str,
        client_id: str,
        service_connection_id: str,
        **kwargs: Any,
    ) -> None:

        self._tenant_id = tenant_id
        self._client_id = client_id
        self._service_connection_id = service_connection_id

        validate_tenant_id(tenant_id)

        self._client_assertion_credential = ClientAssertionCredential(
            tenant_id=tenant_id, client_id=client_id, func=self._get_oidc_token, **kwargs
        )
        self._pipeline = build_pipeline(**kwargs)

    async def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.
        :keyword bool enable_cae: indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Defaults to False.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        validate_env_vars()
        return await self._client_assertion_credential.get_token(
            *scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
        )

    def _get_oidc_token(self) -> str:
        request = build_oidc_request(self._service_connection_id)
        response = self._pipeline.run(request, retry_on_methods=[request.method])
        http_response: HttpResponse = response.http_response
        if http_response.status_code not in [200]:
            raise ClientAuthenticationError(
                message="Unexpected response from OIDC token endpoint.", response=http_response
            )
        json_response = http_response.json()
        if "oidcToken" not in json_response:
            raise ClientAuthenticationError(message="OIDC token not found in response.")
        return json_response["oidcToken"]

    async def __aenter__(self) -> "AzurePipelinesCredential":
        await self._client_assertion_credential.__aenter__()
        self._pipeline.__enter__()
        return self

    async def close(self) -> None:
        """Close the credential's transport session."""
        await self._client_assertion_credential.close()
        self._pipeline.__exit__()
