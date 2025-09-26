# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import TypeVar, Any, MutableMapping, cast, Optional
import logging
import time

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.pipeline.transport import HttpRequest as LegacyHttpRequest
from azure.core.rest import HttpRequest
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError

from .http_constants import HttpHeaders
from ._constants import _Constants as Constants

HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)
# NOTE: This class accesses protected members (_scopes, _token) of the parent class
# to implement fallback and scope-switching logic not exposed by the public API.
# Composition was considered, but still required accessing protected members, so inheritance is retained
# for seamless Azure SDK pipeline integration.
class CosmosBearerTokenCredentialPolicy(BearerTokenCredentialPolicy):
    AadDefaultScope = Constants.AAD_DEFAULT_SCOPE

    def __init__(self, credential, account_scope: str, override_scope: Optional[str] = None,
                 credential_id: Optional[str] = None,
                 client_id: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        self._account_scope = account_scope
        self._override_scope = override_scope
        self._logger = logger or logging.getLogger("azure.cosmos.auth")
        self._current_scope = override_scope or account_scope
        self._client_id = client_id
        self._credential_id = credential_id
        super().__init__(credential, self._current_scope)

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
        start_ns = time.time_ns()
        tried_fallback = False
        activity_id: Optional[str] = None
        while True:
            try:
                super().on_request(request)
                # The None-check for self._token is done in the parent on_request
                self._update_headers(request.http_request.headers, cast(AccessToken, self._token).token)
                if request and request.http_request and request.http_request.headers:
                    activity_id = request.http_request.headers.get(HttpHeaders.ActivityId)
                end_ns = time.time_ns()
                self._logger.info("cosmos client sync auth on_request success | account_name: %s "
                                  "| scope: %s | duration_ns: %s "
                                  "| activity_id: %s"
                                  "| client_id: %s"
                                  "| credential_id: %s",
                                  str(self._account_scope), str(self._current_scope),
                                  str(end_ns - start_ns), str(activity_id),
                                  str(self._client_id),
                                  str(self._credential_id))
                break
            except HttpResponseError as ex:
                if request and request.http_request and request.http_request.headers:
                    activity_id = request.http_request.headers.get(HttpHeaders.ActivityId)
                status_code = getattr(ex, 'status_code', None)
                sub_status_code = getattr(ex, 'sub_status_code', None)
                self._logger.warning("cosmos client sync auth on_request HttpResponseError | "
                                     "account_name: %s | scope: %s | "
                                     "activity_id: %s | status_code: %s | sub_status: %s",
                                     "| client_id: %s"
                                     "| credential_id: %s",
                                     str(self._account_scope),
                                     str(self._current_scope), str(activity_id),
                                     str(status_code), str(sub_status_code),
                                     str(self._client_id),
                                     str(self._credential_id))
                # Only fallback if not using override, not already tried, and error is AADSTS500011
                if (
                        not self._override_scope and
                        not tried_fallback and
                        self._current_scope != self.AadDefaultScope and
                        "AADSTS500011" in str(ex)
                ):
                    self._scopes = (self.AadDefaultScope,)
                    self._current_scope = self.AadDefaultScope
                    tried_fallback = True
                    continue
                raise

    def authorize_request(self, request: PipelineRequest[HTTPRequestType], *scopes: str, **kwargs: Any) -> None:
        """Acquire a token from the credential and authorize the request with it.

        Keyword arguments are passed to the credential's get_token method. The token will be cached and used to
        authorize future requests.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        :param str scopes: required scopes of authentication
        """
        start_ns = time.time_ns()

        super().authorize_request(request, *scopes, **kwargs)
        # The None-check for self._token is done in the parent authorize_request
        self._update_headers(request.http_request.headers, cast(AccessToken, self._token).token)
        end_ns = time.time_ns()
        activity_id: Optional[str] = None
        if request and request.http_request and request.http_request.headers:
            activity_id = request.http_request.headers.get(HttpHeaders.ActivityId)
        self._logger.info("cosmos client sync auth authorize_request success | account_name: %s "
                          "| scope: %s | duration_ns: %s "
                          "| activity_id: %s"
                          "| client_id: %s"
                          "| credential_id: %s",
                          str(self._account_scope), str(self._current_scope),
                          str(end_ns - start_ns), str(activity_id),
                          str(self._client_id),
                          str(self._credential_id))
