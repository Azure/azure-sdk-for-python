# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
from typing import Any, List, Optional
# pylint: disable=non-abstract-transport-import
# pylint: disable=no-name-in-module
from azure.core.pipeline.transport import RequestsTransport
from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import TokenCredential
from azure.core.pipeline.policies import RetryPolicy
from .entra_token_guard_policy import EntraTokenGuardPolicy
from . import token_utils


class TokenExchangeClient:
    """Represents a client that exchanges an Entra token for an Azure Communication Services (ACS) token.
    
    :param resource_endpoint: The endpoint URL of the resource to authenticate against.
    :param credential: The credential to use for token exchange.
    :param scopes: The scopes to request during the token exchange.
    :keyword transport: Optional transport to use for the pipeline.
    """

    # pylint: disable=C4748
    # pylint: disable=client-method-missing-type-annotations
    def __init__(
            self,
            resource_endpoint: str,
            credential: TokenCredential,
            scopes: Optional[List[str]] = None,
            **kwargs: Any):

        self._resource_endpoint = resource_endpoint
        self._scopes = scopes or ["https://communication.azure.com/clients/.default"]
        self._credential = credential
        pipeline_transport = kwargs.get("transport", None)
        self._pipeline = self._create_pipeline_from_options(pipeline_transport)

    def _create_pipeline_from_options(self, pipeline_transport):
        auth_policy = BearerTokenCredentialPolicy(self._credential, *self._scopes)
        entra_token_guard_policy = EntraTokenGuardPolicy()
        retry_policy = RetryPolicy()
        policies = [auth_policy, entra_token_guard_policy, retry_policy]
        if pipeline_transport:
            return Pipeline(policies=policies, transport=pipeline_transport)
        return Pipeline(policies=policies, transport=RequestsTransport())

    def exchange_entra_token(self) -> AccessToken:
        message = token_utils.create_request_message(self._resource_endpoint, self._scopes)
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
                expires_on_epoch = token_utils.parse_expires_on(expires_on, response)
                if expires_on_epoch is None:
                    raise ValueError("Failed to parse 'expiresOn' value from access token response")
                return AccessToken(token, expires_on_epoch)
            except Exception as ex:
                raise ValueError("Failed to parse access token from response") from ex
        else:
            raise HttpResponseError(
                message="Failed to exchange Entra token for ACS token",
                response=response.http_response
            )
