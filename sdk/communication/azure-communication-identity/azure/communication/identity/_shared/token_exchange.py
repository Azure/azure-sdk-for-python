# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
from datetime import datetime, timezone
from dateutil.parser import isoparse
from typing import Tuple, Any
from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError

from entra_token_guard_policy import EntraTokenGuardPolicy, AsyncEntraTokenGuardPolicy
from entra_token_credential_options import EntraCommunicationTokenCredentialOptions, AsyncEntraCommunicationTokenCredentialOptions

TEAMS_EXTENSION_SCOPE_PREFIX = "https://auth.msft.communication.azure.com/"
COMMUNICATION_CLIENTS_SCOPE_PREFIX = "https://communication.azure.com/clients/"
TEAMS_EXTENSION_ENDPOINT = "/access/teamsPhone/:exchangeAccessToken"
TEAMS_EXTENSION_API_VERSION = "2025-03-02-preview"
COMMUNICATION_CLIENTS_ENDPOINT = "/access/entra/:exchangeAccessToken"
COMMUNICATION_CLIENTS_API_VERSION = "2024-04-01-preview"

class TokenExchangeClient:
    """Represents a client that exchanges an Entra token for an Azure Communication Services (ACS) token."""

    def __init__(self, options: EntraCommunicationTokenCredentialOptions, pipeline_transport: Any = None):
        self._resource_endpoint = options.resource_endpoint
        self._scopes = options.scopes
        self._token_credential = options.token_credential
        self._pipeline = self._create_pipeline_from_options(options, pipeline_transport)
        #self._access_token_cache = None  # Could be implemented as a custom cache if needed

    def _create_pipeline_from_options(self, options, pipeline_transport):
        auth_policy = BearerTokenCredentialPolicy(options.token_credential, options.scopes)
        entra_token_guard_policy = EntraTokenGuardPolicy()
        policies = [auth_policy, entra_token_guard_policy]
        if pipeline_transport:
            return Pipeline(policies=policies, transport=pipeline_transport)
        from azure.core.pipeline.transport import RequestsTransport
        return Pipeline(policies=policies, transport=RequestsTransport())

    def _exchange_entra_token(self) -> AccessToken:
        message = self._create_request_message()
        response = self._pipeline.run(message)
        return self._parse_access_token_from_response(response)

    def _create_request_message(self) -> Any:
        from azure.core.pipeline.transport import HttpRequest
        request_uri = self._create_request_uri()
        request = HttpRequest("POST", request_uri)
        request.headers["Accept"] = "application/json"
        request.headers["Content-Type"] = "application/json"
        request.set_json_body({})
        return request

    def _create_request_uri(self) -> str:
        endpoint, api_version = self._determine_endpoint_and_api_version()
        base = self._resource_endpoint.rstrip("/")
        return f"{base}{endpoint}?api-version={api_version}"

    def _determine_endpoint_and_api_version(self) -> Tuple[str, str]:
        if not self._scopes or not isinstance(self._scopes, list):
            raise ValueError(
                f"Scopes validation failed. Ensure all scopes start with either {TEAMS_EXTENSION_SCOPE_PREFIX} or {COMMUNICATION_CLIENTS_SCOPE_PREFIX}."
            )
        if all(scope.startswith(TEAMS_EXTENSION_SCOPE_PREFIX) for scope in self._scopes):
            return TEAMS_EXTENSION_ENDPOINT, TEAMS_EXTENSION_API_VERSION
        elif all(scope.startswith(COMMUNICATION_CLIENTS_SCOPE_PREFIX) for scope in self._scopes):
            return COMMUNICATION_CLIENTS_ENDPOINT, COMMUNICATION_CLIENTS_API_VERSION
        else:
            raise ValueError(
                f"Scopes validation failed. Ensure all scopes start with either {TEAMS_EXTENSION_SCOPE_PREFIX} or {COMMUNICATION_CLIENTS_SCOPE_PREFIX}."
            )

    def _parse_access_token_from_response(self, response: PipelineResponse) -> AccessToken:
        if response.http_response.status_code == 200:
            try:
                content = response.http_response.text()
                data = json.loads(content)
                access_token_json = data["accessToken"]
                token = access_token_json["token"]
                expires_on = access_token_json["expiresOn"]

                return AccessToken(token, expires_on)
            except Exception as ex:
                raise ClientAuthenticationError("Failed to parse access token from response") from ex
        else:
            raise HttpResponseError(
                message="Failed to exchange Entra token for ACS token",
                response=response.http_response
            )