# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from time import time

from azure.core import Configuration, HttpRequest
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import ContentDecodePolicy, NetworkTraceLoggingPolicy, RetryPolicy
from azure.core.pipeline.transport import RequestsTransport
from msal import TokenCache

from .exceptions import AuthenticationError

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, Iterable, Mapping, Optional


class _AuthnClientBase(object):
    def __init__(self, auth_url, **kwargs):
        if not auth_url:
            raise ValueError("auth_url")
        super(_AuthnClientBase, self).__init__(**kwargs)
        self._cache = TokenCache()
        self._auth_url = auth_url

    def get_cached_token(self, scopes):
        # type: (Iterable[str]) -> Optional[str]
        tokens = self._cache.find(TokenCache.CredentialType.ACCESS_TOKEN, list(scopes))
        for token in tokens:
            if all((scope in token["target"] for scope in scopes)):
                if int(token["expires_on"]) - 300 > int(time()):
                    return token["secret"]
        return None

    def _prepare_request(self, method="POST", form_data=None, params=None):
        request = HttpRequest(method, self._auth_url)
        if form_data:
            request.headers["Content-Type"] = "application/x-www-form-urlencoded"
            request.set_formdata_body(form_data)
        if params:
            request.format_parameters(params)
        return request

    def _deserialize_and_cache_token(self, response, scopes):
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


class AuthnClient(_AuthnClientBase):
    def __init__(self, auth_url, config=None, policies=None, transport=None, **kwargs):
        config = config or self.create_config(**kwargs)
        # TODO: ContentDecodePolicy doesn't accept kwargs
        policies = policies or [ContentDecodePolicy(), config.logging_policy, config.retry_policy]
        if not transport:
            transport = RequestsTransport(configuration=config)
        self._pipeline = Pipeline(transport=transport, policies=policies)
        super(AuthnClient, self).__init__(auth_url, **kwargs)

    def request_token(self, scopes, method="POST", form_data=None, params=None):
        request = self._prepare_request(method, form_data, params)
        response = self._pipeline.run(request, stream=False)
        token = self._deserialize_and_cache_token(response, scopes)
        return token

    @staticmethod
    def create_config(**kwargs):
        # type: (Mapping[str, Any]) -> Configuration
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = RetryPolicy(retry_on_status_codes=[404, 429] + [x for x in range(500, 600)], **kwargs)
        return config
