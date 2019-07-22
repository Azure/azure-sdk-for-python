# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import calendar
import time

from azure.core import Configuration, HttpRequest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import ContentDecodePolicy, NetworkTraceLoggingPolicy, RetryPolicy
from azure.core.pipeline.transport import HttpTransport, RequestsTransport
from msal import TokenCache

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
if TYPE_CHECKING:
    from time import struct_time
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
        # type: (Iterable[str]) -> Optional[AccessToken]
        tokens = self._cache.find(TokenCache.CredentialType.ACCESS_TOKEN, list(scopes))
        for token in tokens:
            if all((scope in token["target"] for scope in scopes)):
                expires_on = int(token["expires_on"])
                if expires_on - 300 > int(time.time()):
                    return AccessToken(token["secret"], expires_on)
        return None

    def _deserialize_and_cache_token(self, response, scopes, request_time):
        # type: (PipelineResponse, Iterable[str], int) -> AccessToken

        # ContentDecodePolicy sets this, and should have raised if it couldn't deserialize the response
        payload = response.context[ContentDecodePolicy.CONTEXT_NAME]

        if not payload or "access_token" not in payload or not ("expires_in" in payload or "expires_on" in payload):
            if payload and "access_token" in payload:
                payload["access_token"] = "****"
            raise ClientAuthenticationError(message="Unexpected response '{}'".format(payload))

        token = payload["access_token"]

        # AccessToken wants expires_on as an int
        expires_on = payload.get("expires_on") or int(payload["expires_in"]) + request_time
        try:
            expires_on = int(expires_on)
        except ValueError:
            # probably an App Service MSI response, convert it to epoch seconds
            try:
                t = self._parse_app_service_expires_on(expires_on)
                expires_on = calendar.timegm(t)
            except ValueError:
                # have a token but don't know when it expires -> treat it as single-use
                expires_on = request_time

        # now we have an int expires_on, ensure the cache entry gets it
        payload["expires_on"] = expires_on

        self._cache.add({"response": payload, "scope": scopes})

        return AccessToken(token, expires_on)

    @staticmethod
    def _parse_app_service_expires_on(expires_on):
        # type: (str) -> struct_time
        """
        Parse expires_on from an App Service MSI response (e.g. "06/19/2019 23:42:01 +00:00") to struct_time.
        Expects the time is given in UTC (i.e. has offset +00:00).
        """
        if not expires_on.endswith(" +00:00"):
            raise ValueError("'{}' doesn't match expected format".format(expires_on))

        # parse the string minus the timezone offset
        return time.strptime(expires_on[: -len(" +00:00")], "%m/%d/%Y %H:%M:%S")

    # TODO: public, factor out of request_token
    def _prepare_request(self, method="POST", headers=None, form_data=None, params=None):
        # type: (Optional[str], Optional[Mapping[str, str]], Optional[Mapping[str, str]], Optional[Dict[str, str]]) -> HttpRequest
        request = HttpRequest(method, self._auth_url, headers=headers)
        if form_data:
            request.headers["Content-Type"] = "application/x-www-form-urlencoded"
            request.set_formdata_body(form_data)
        if params:
            request.format_parameters(params)
        return request


class AuthnClient(AuthnClientBase):
    """
    Synchronous authentication client.

    :param str auth_url:
    :param config: Optional configuration for the HTTP pipeline.
    :type config: :class:`azure.core.configuration`
    :param policies: Optional policies for the HTTP pipeline.
    :type policies:
    :param transport: Optional HTTP transport.
    :type transport:
    """

    def __init__(self, auth_url, config=None, policies=None, transport=None, **kwargs):
        # type: (str, Optional[Configuration], Optional[Iterable[HTTPPolicy]], Optional[HttpTransport], Mapping[str, Any]) -> None
        config = config or self.create_config(**kwargs)
        policies = policies or [ContentDecodePolicy(), config.logging_policy, config.retry_policy]
        if not transport:
            transport = RequestsTransport(**kwargs)
        self._pipeline = Pipeline(transport=transport, policies=policies)
        super(AuthnClient, self).__init__(auth_url, **kwargs)

    def request_token(self, scopes, method="POST", headers=None, form_data=None, params=None, **kwargs):
        # type: (Iterable[str], Optional[str], Optional[Mapping[str, str]], Optional[Mapping[str, str]], Optional[Dict[str, str]], Any) -> AccessToken
        request = self._prepare_request(method, headers=headers, form_data=form_data, params=params)
        request_time = int(time.time())
        response = self._pipeline.run(request, stream=False, **kwargs)
        token = self._deserialize_and_cache_token(response, scopes, request_time)
        return token

    @staticmethod
    def create_config(**kwargs):
        # type: (Mapping[str, Any]) -> Configuration
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        return config
