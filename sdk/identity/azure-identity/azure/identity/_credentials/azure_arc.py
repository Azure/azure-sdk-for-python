# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import time
from typing import TYPE_CHECKING

from azure.core.configuration import Configuration
from azure.core.pipeline import PipelineRequest, PipelineResponse
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

        client_args = _get_client_args(self, **kwargs)
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


def _get_policies(credential, config, **kwargs):
    # type: (AzureArcCredential, Configuration, **Any) -> List[PolicyType]
    return [
        HeadersPolicy(**kwargs),
        UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs),
        config.proxy_policy,
        config.retry_policy,
        NetworkTraceLoggingPolicy(**kwargs),
        DistributedTracingPolicy(**kwargs),
        HttpLoggingPolicy(**kwargs),
        ArcChallengeAuthPolicy(credential),
    ]


def _get_client_args(credential, **kwargs):
    # type: (AzureArcCredential, **Any) -> Optional[dict]
    identity_config = kwargs.pop("_identity_config", None) or {}

    url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
    if not url:
        # Azure Arc managed identity isn't available in this environment
        return None

    config = _get_configuration()

    return dict(
        kwargs,
        _identity_config=identity_config,
        policies=_get_policies(credential, config),
        request_factory=functools.partial(_get_request, url),
    )


def _get_request(url, scope, identity_config):
    # type: (str, str, dict) -> HttpRequest
    request = HttpRequest("GET", url)
    request.format_parameters(dict({"api-version": "2019-08-15", "resource": scope}, **identity_config))
    return request


def _update_headers(request, secret_key=None):
    # type: (PipelineRequest, str) -> PipelineRequest
    request.http_request.headers = {"Metadata": "true"}
    if secret_key:
        request.http_request.headers["Authorization"] = "Basic {}".format(secret_key)

    return request


def _get_secret_key(response):
    # type: (PipelineResponse) -> str
    # expecting header containing path to secret key file
    header = response.http_response.headers.get("Www-Authenticate")
    if header is None:
        raise CredentialUnavailableError(message="Did not receive a value from Www-Authenticate header")

    secret_key = None

    # expecting header with structure like 'Basic realm=<file path>'
    key_file = header.split("=")[1]
    with open(key_file, "r") as file:
        try:
            secret_key = file.read()
        except Exception as error:  # pylint:disable=broad-except
            # user is expected to have obtained read permission prior to this being called
            raise CredentialUnavailableError(message="Could not read file {} contents: {}".format(key_file, error))

    return secret_key


class _ArcChallengeAuthPolicyBase(object):
    """Sans I/O base for Azure Arc's challenge authentication policy"""

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._token = None  # type: Optional[AccessToken]
        super(_ArcChallengeAuthPolicyBase, self).__init__(**kwargs)

    @property
    def _need_new_token(self):
        # type: () -> bool
        return not self._token or self._token.expires_on - time.time() < 300


class ArcChallengeAuthPolicy(_ArcChallengeAuthPolicyBase, HTTPPolicy):
    """Policy for handling Azure Arc's challenge authentication"""

    def __init__(self, credential, **kwargs):
        # type: (AzureArcCredential, **Any) -> None
        self._credential = credential
        self._scope = None
        self._secret_key = None
        super(ArcChallengeAuthPolicy, self).__init__(**kwargs)

    def send(self, request):
        # type: (PipelineRequest) -> HttpResponse
        if self._scope is None:
            self._scope = request.http_request.query.get("resource")

        request = _update_headers(request)
        response = self.next.send(request)

        if response.http_response.status_code == 401:
            self._secret_key = _get_secret_key(response)
            request = _update_headers(request, secret_key=self._secret_key)
            response = self.next.send(request)

        return response
