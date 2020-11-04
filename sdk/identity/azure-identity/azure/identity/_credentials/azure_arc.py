# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import copy
import functools
import os
import time
from typing import TYPE_CHECKING

from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.core.pipeline.policies import (
    DistributedTracingPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    HTTPPolicy,
    UserAgentPolicy,
    NetworkTraceLoggingPolicy,
)

from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal.managed_identity_client import ManagedIdentityClient, _get_configuration
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.user_agent import USER_AGENT

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, List, Optional, Union
    from azure.core.credentials import AccessToken
    from azure.core.pipeline.policies import SansIOHTTPPolicy

    PolicyType = Union[HTTPPolicy, SansIOHTTPPolicy]


class AzureArcCredential(GetTokenMixin):
    def __init__(self, **kwargs):
        # type: (**Any) -> None
        super(AzureArcCredential, self).__init__()

        client_args = self._get_client_args(**kwargs)
        if client_args:
            self._client = ManagedIdentityClient(**client_args)
        else:
            self._client = None

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        if not self._client:
            raise CredentialUnavailableError(
                message="Azure Arc managed identity configuration not found in environment"
            )
        return super(AzureArcCredential, self).get_token(*scopes, **kwargs)

    def _acquire_token_silently(self, *scopes):
        # type: (*str) -> Optional[AccessToken]
        return self._client.get_cached_token(*scopes)

    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        return self._client.request_token(*scopes, **kwargs)

    def _get_policies(self, config, **kwargs):
        return [
            HeadersPolicy(**kwargs),
            UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs),
            config.proxy_policy,
            config.retry_policy,
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
            ArcChallengeAuthPolicy(self)
        ]

    def _get_client_args(self, **kwargs):
        # type: (**Any) -> Optional[dict]
        identity_config = kwargs.pop("_identity_config", None) or {}

        url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
        if not url:
            # Azure Arc managed identity isn't available in this environment
            return None

        config = _get_configuration()

        return dict(
            kwargs,
            _identity_config=identity_config,
            policies=self._get_policies(config),
            request_factory=functools.partial(_get_request, url),
        )


def _get_request(url, scope, identity_config):
    # type: (str, str, dict) -> HttpRequest
    request = HttpRequest("GET", url)
    request.format_parameters(dict({"api-version": "2019-08-15", "resource": scope}, **identity_config))
    return request


def _enforce_https(request):
    # type: (PipelineRequest) -> None
    if not request.http_request.url.lower().startswith("https"):
        raise ServiceRequestError(
            "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
        )


def _update_headers(request, **kwargs):
    # type: (PipelineRequest, **Any) -> PipelineRequest
    request.http_request.headers = {"Metadata": "true"}

    secret_key = kwargs.pop("secret_key", None)
    if secret_key:
        request.http_request.headers["Authorization"] = "Basic {}".format(secret_key)

    token = kwargs.pop("token", None)
    if token:
        request.http_request.headers["Authorization"] = "Bearer {}".format(token)

    return request


class _ArcChallengeAuthPolicyBase(object):
    """Sans I/O base for challenge authentication policies"""

    def __init__(self, **kwargs):
        self._token = None  # type: Optional[AccessToken]
        super(_ArcChallengeAuthPolicyBase, self).__init__(**kwargs)

    @property
    def _need_new_token(self):
        # type: () -> bool
        return not self._token or self._token.expires_on - time.time() < 300


class ArcChallengeAuthPolicy(_ArcChallengeAuthPolicyBase, HTTPPolicy):
    """policy for handling HTTP authentication challenges"""

    def __init__(self, credential, **kwargs):
        # type: (AzureArcCredential, **Any) -> None
        self._credential = credential
        self._scope = None
        self._secret_key = None
        super(ArcChallengeAuthPolicy, self).__init__(**kwargs)

    def send(self, request):
        # type: (PipelineRequest) -> HttpResponse
        _enforce_https(request)
        self.on_challenge(request)
        response = self.next.send(request)

        if response.http_response.status_code == 401:
            # expecting header containing path to secret key file
            header = response.http_response.headers.get("Www-Authenticate")
            if not header:
                raise CredentialUnavailableError(
                    message="Did not receive a value from Www-Authenticate header"
                )

            key_file = header.split("=")[1]
            with open(key_file, 'r') as file:
                try:
                    self._secret_key = file.read()
                except Exception as error:  # pylint:disable=broad-except
                    raise CredentialUnavailableError(
                        message="Could not read file {} contents: {}".format(key_file, error)
                    )

            _update_headers(request, secret_key=self._secret_key)
            response = self.next.send(request)

        return response

    def on_challenge(self, request):
        # type: (PipelineRequest) -> None
        """authenticate according to challenge, add Authorization header to request"""

        if self._need_new_token:
            self._scope = request.http_request.query.get("resource")
            self._token = self._credential.get_token(*self._scope)

        _update_headers(request, token=self._token.token)
