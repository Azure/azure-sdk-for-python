# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
from typing import Tuple, Any
from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from .entra_token_guard_policy import EntraTokenGuardPolicy, AsyncEntraTokenGuardPolicy
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.credentials import TokenCredential
from typing import List, Optional
from dateutil import parser as dateutil_parser  # type: ignore

from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline import AsyncPipeline, PipelineResponse


TEAMS_EXTENSION_SCOPE_PREFIX = "https://auth.msft.communication.azure.com/"
COMMUNICATION_CLIENTS_SCOPE_PREFIX = "https://communication.azure.com/clients/"
TEAMS_EXTENSION_ENDPOINT = "/access/teamsExtension/:exchangeAccessToken"
TEAMS_EXTENSION_API_VERSION = "2025-06-30"
COMMUNICATION_CLIENTS_ENDPOINT = "/access/entra/:exchangeAccessToken"
COMMUNICATION_CLIENTS_API_VERSION = "2025-03-02-preview"

class TokenExchangeClient:
    """Represents a client that exchanges an Entra token for an Azure Communication Services (ACS) token."""

    def __init__(self, resource_endpoint: str, token_credential: TokenCredential, scopes: Optional[List[str]] = None, pipeline_transport: Any = None):
        self._resource_endpoint = resource_endpoint
        self._scopes = scopes or ["https://communication.azure.com/clients/.default"]
        self._token_credential = token_credential
        self._pipeline = self._create_pipeline_from_options(pipeline_transport)

    def _create_pipeline_from_options(self, pipeline_transport):
        auth_policy = BearerTokenCredentialPolicy(self._token_credential, *self._scopes)
        entra_token_guard_policy = EntraTokenGuardPolicy()
        policies = [auth_policy, entra_token_guard_policy]
        if pipeline_transport:
            return Pipeline(policies=policies, transport=pipeline_transport)
        from azure.core.pipeline.transport import RequestsTransport
        return Pipeline(policies=policies, transport=RequestsTransport())

    def exchange_entra_token(self) -> AccessToken:
        message = _TokenExchangeUtils.create_request_message(self._resource_endpoint, self._scopes)
        response = self._pipeline.run(message)
        return self._parse_access_token_from_response(response)

    def _parse_access_token_from_response(self, response: PipelineResponse) -> AccessToken:
        if response.http_response.status_code == 200:
            try:
                content = response.http_response.text()
                data = json.loads(content)
                access_token_json = data["accessToken"]
                token = access_token_json["token"]
                expires_on = access_token_json["expiresOn"]
                expires_on_epoch = _TokenExchangeUtils.parse_expires_on(expires_on, response)
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

class AsyncTokenExchangeClient:
    """Asynchronous client that exchanges an Entra token for an Azure Communication Services (ACS) token."""

    def __init__(
        self,
        resource_endpoint: str,
        token_credential: AsyncTokenCredential,
        scopes: Optional[List[str]] = None,
        pipeline_transport: Any = None
    ):
        self._resource_endpoint = resource_endpoint
        self._scopes = scopes or ["https://communication.azure.com/clients/.default"]
        self._token_credential = token_credential
        self._pipeline = self._create_pipeline_from_options(pipeline_transport)

    def _create_pipeline_from_options(self, pipeline_transport):
        auth_policy = AsyncBearerTokenCredentialPolicy(self._token_credential, *self._scopes)
        entra_token_guard_policy = AsyncEntraTokenGuardPolicy()
        policies = [auth_policy, entra_token_guard_policy]
        if pipeline_transport:
            return AsyncPipeline(policies=policies, transport=pipeline_transport)
        from azure.core.pipeline.transport import AioHttpTransport
        return AsyncPipeline(policies=policies, transport=AioHttpTransport())

    async def exchange_entra_token(self) -> AccessToken:
        message = _TokenExchangeUtils.create_request_message(self._resource_endpoint, self._scopes)
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
                expires_on_epoch = _TokenExchangeUtils.parse_expires_on(expires_on, response)
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

class _TokenExchangeUtils:
        @staticmethod
        def create_request_message(resource_endpoint: str, scopes: Optional[List[str]]) -> Any:
            from azure.core.pipeline.transport import HttpRequest
            request_uri = _TokenExchangeUtils.create_request_uri(resource_endpoint, scopes)
            request = HttpRequest("POST", request_uri)
            request.headers["Accept"] = "application/json"
            request.headers["Content-Type"] = "application/json"
            request.set_json_body({})
            return request

        @staticmethod
        def create_request_uri(resource_endpoint: str, scopes: Optional[List[str]]) -> str:
            endpoint, api_version = _TokenExchangeUtils.determine_endpoint_and_api_version(scopes)
            base = resource_endpoint.rstrip("/")
            return f"{base}{endpoint}?api-version={api_version}"

        @staticmethod
        def determine_endpoint_and_api_version(scopes: Optional[List[str]]) -> Tuple[str, str]:
            if not scopes or not isinstance(scopes, list):
                raise ValueError(
                    f"Scopes validation failed. Ensure all scopes start with either {TEAMS_EXTENSION_SCOPE_PREFIX} or {COMMUNICATION_CLIENTS_SCOPE_PREFIX}."
                )
            if all(scope.startswith(TEAMS_EXTENSION_SCOPE_PREFIX) for scope in scopes):
                return TEAMS_EXTENSION_ENDPOINT, TEAMS_EXTENSION_API_VERSION
            elif all(scope.startswith(COMMUNICATION_CLIENTS_SCOPE_PREFIX) for scope in scopes):
                return COMMUNICATION_CLIENTS_ENDPOINT, COMMUNICATION_CLIENTS_API_VERSION
            else:
                raise ValueError(
                    f"Scopes validation failed. Ensure all scopes start with either {TEAMS_EXTENSION_SCOPE_PREFIX} or {COMMUNICATION_CLIENTS_SCOPE_PREFIX}."
                )

        @staticmethod
        def parse_expires_on(expires_on, response):
            if isinstance(expires_on, str):
                try:
                    expires_on_dt = dateutil_parser.parse(expires_on)
                    expires_on_epoch = int(expires_on_dt.timestamp())
                    return expires_on_epoch
                except Exception as ex:
                    raise HttpResponseError(
                    message="Unknown format for expires_on field in access token response",
                    response=response.http_response)
            else:
                raise HttpResponseError(
                    message="Missing expires_on field in access token response",
                    response=response.http_response)
            

            