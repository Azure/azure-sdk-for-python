# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import TypeVar, Any, MutableMapping, cast, Optional

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.pipeline.transport import HttpRequest as LegacyHttpRequest
from azure.core.rest import HttpRequest
from azure.core.credentials import AccessToken

from .http_constants import HttpHeaders

HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)


class CosmosBearerTokenCredentialPolicy(BearerTokenCredentialPolicy):
    AadDefaultScope = "https://cosmos.azure.com/.default"

    def __init__(self, credential, account_scope: str, override_scope: Optional[str] = None):
        self._account_scope = account_scope
        self._override_scope = override_scope
        self._primary_policy = BearerTokenCredentialPolicy(credential, override_scope or account_scope)
        self._fallback_policy = (
            None if override_scope else BearerTokenCredentialPolicy(credential, self.AadDefaultScope)
        )
        self._use_fallback = False

    @staticmethod
    def _update_headers(headers: MutableMapping[str, str], token: str) -> None:
        """Updates the Authorization header with the bearer token.

        :param MutableMapping[str, str] headers: The HTTP Request headers
        :param str token: The OAuth token.
        """
        headers[HttpHeaders.Authorization] = f"type=aad&ver=1.0&sig={token}"

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        """Called before the policy sends a request.

        The base implementation authorizes the request with a bearer token.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        """
        policy = self._fallback_policy if self._use_fallback else self._primary_policy
        try:
            policy.on_request(request)
            self._update_headers(request.http_request.headers, cast(AccessToken, policy._token).token)
        except Exception as ex:
            # Only fallback if not using override, and error is AADSTS500011
            if (
                    self._fallback_policy is not None
                    and not self._use_fallback
                    and "AADSTS500011" in str(ex)
            ):
                self._use_fallback = True
                self._fallback_policy.on_request(request)
                self._update_headers(request.http_request.headers,
                                     cast(AccessToken, self._fallback_policy._token).token)
            else:
                raise

    def authorize_request(self, request: PipelineRequest[HTTPRequestType], *scopes: str, **kwargs: Any) -> None:
        """Acquire a token from the credential and authorize the request with it.

        Keyword arguments are passed to the credential's get_token method. The token will be cached and used to
        authorize future requests.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        :param str scopes: required scopes of authentication
        """

        policy = self._fallback_policy if self._use_fallback else self._primary_policy
        policy.authorize_request(request, *scopes, **kwargs)
        # The None-check for self._token is done in the parent authorize_request
        self._update_headers(request.http_request.headers, cast(AccessToken, policy._token).token)
