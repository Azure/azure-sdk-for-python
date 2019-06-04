# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from time import time

from azure.core import Configuration, HttpRequest
from azure.core.pipeline import Pipeline, PipelineRequest
from azure.core.pipeline.policies import ContentDecodePolicy, NetworkTraceLoggingPolicy, RetryPolicy
from azure.core.pipeline.transport import HttpTransport, RequestsTransport
from msal import TokenCache

from .exceptions import AuthenticationError

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, Dict, Iterable, Mapping, Optional
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.policies import HTTPPolicy


class AuthnClientBase(object):
    """Sans I/O authentication client methods"""

    def __init__(self, auth_url, **kwargs):
        # type: (str, Mapping[str, Any]) -> None
        if not auth_url:
            raise ValueError("auth_url should be the URL of an OAuth endpoint")
        super(AuthnClientBase, self).__init__()
        self._auth_url = auth_url
        self._cache = TokenCache()

    def get_cached_token(self, scopes):
        # type: (Iterable[str]) -> Optional[str]
        tokens = self._cache.find(TokenCache.CredentialType.ACCESS_TOKEN, list(scopes))
        for token in tokens:
            if all((scope in token["target"] for scope in scopes)):
                if int(token["expires_on"]) - 300 > int(time()):
                    return token["secret"]
        return None

    def _deserialize_and_cache_token(self, response, scopes):
        # type: (PipelineResponse, Iterable[str]) -> str
        try:
            if "deserialized_data" in response.context:
                payload = response.context["deserialized_data"]
            else:
                payload = response.http_response.text()
            token = payload["access_token"]
            self._cache.add({"response": payload, "scope": scopes})
            return token
        except KeyError:
            raise AuthenticationError("Unexpected authentication response: {}".format(payload))
        except Exception as ex:
            raise AuthenticationError("Authentication failed: {}".format(str(ex)))

    def _prepare_request(self, method="POST", form_data=None, params=None):
        # type: (Optional[str], Optional[Mapping[str, str]], Optional[Dict[str, str]]) -> HttpRequest
        request = HttpRequest(method, self._auth_url)
        if form_data:
            request.headers["Content-Type"] = "application/x-www-form-urlencoded"
            request.set_formdata_body(form_data)
        if params:
            request.format_parameters(params)
        return request


class AuthnClient(AuthnClientBase):
    """Synchronous authentication client"""

    def __init__(self, auth_url, config=None, policies=None, transport=None, **kwargs):
        # type: (str, Optional[Configuration], Optional[Iterable[HTTPPolicy]], Optional[HttpTransport], Mapping[str, Any]) -> None
        config = config or self.create_config(**kwargs)
        policies = policies or [ContentDecodePolicy(), config.logging_policy, config.retry_policy]
        if not transport:
            transport = RequestsTransport(configuration=config)
        self._pipeline = Pipeline(transport=transport, policies=policies)
        super(AuthnClient, self).__init__(auth_url, **kwargs)

    def request_token(self, scopes, method="POST", form_data=None, params=None):
        # type: (Iterable[str], Optional[str], Optional[Mapping[str, str]], Optional[Dict[str, str]]) -> str
        request = self._prepare_request(method, form_data, params)
        response = self._pipeline.run(request, stream=False)
        token = self._deserialize_and_cache_token(response, scopes)
        return token

    @staticmethod
    def create_config(**kwargs):
        # type: (Mapping[str, Any]) -> Configuration
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = RetryPolicy(retry_on_status_codes=[404, 429] + list(range(500, 600)), **kwargs)
        return config
