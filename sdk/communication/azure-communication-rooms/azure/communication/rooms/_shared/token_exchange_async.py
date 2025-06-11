# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
from typing import Any
from typing import List, Optional
from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline, PipelineResponse
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.credentials_async import AsyncTokenCredential
from .entra_token_guard_policy_async import EntraTokenGuardPolicy
from .token_exchange_utils import TokenExchangeUtils


class TokenExchangeClient:
    """Asynchronous client that exchanges an Entra token for an Azure Communication Services (ACS) token."""

    def __init__(
            self,
            resource_endpoint: str,
            token_credential: AsyncTokenCredential,
            scopes: Optional[List[str]] = None,
            pipeline_transport: Any = None):

        self._resource_endpoint = resource_endpoint
        self._scopes = scopes or ["https://communication.azure.com/clients/.default"]
        self._token_credential = token_credential
        self._pipeline = self._create_pipeline_from_options(pipeline_transport)

    def _create_pipeline_from_options(self, pipeline_transport):
        auth_policy = AsyncBearerTokenCredentialPolicy(self._token_credential, *self._scopes)
        entra_token_guard_policy = EntraTokenGuardPolicy()
        policies = [auth_policy, entra_token_guard_policy]
        if pipeline_transport:
            return AsyncPipeline(policies=policies, transport=pipeline_transport)
        from azure.core.pipeline.transport import AioHttpTransport
        return AsyncPipeline(policies=policies, transport=AioHttpTransport())

    async def exchange_entra_token(self) -> AccessToken:
        message = TokenExchangeUtils.create_request_message(self._resource_endpoint, self._scopes)
        response = await self._pipeline.run(message)
        return await self._parse_access_token_from_response(response)

    async def _parse_access_token_from_response(self, response: PipelineResponse) -> AccessToken:
        if response.http_response.status_code == 200:
            try:
                content = response.http_response.text()
                data = json.loads(content)
                access_token_json = data["accessToken"]
                token = access_token_json["token"]
                expires_on = access_token_json["expiresOn"]
                expires_on_epoch = TokenExchangeUtils.parse_expires_on(expires_on, response)
                if expires_on_epoch is None:
                    raise ClientAuthenticationError("Failed to parse 'expiresOn' value from access token response")
                return AccessToken(token, expires_on_epoch)
            except Exception as ex:
                raise ClientAuthenticationError("Failed to parse access token from response") from ex
        else:
            raise HttpResponseError(
                message="Failed to exchange Entra token for ACS token",
                response=response.http_response
            )
