# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import calendar
import time

from azure.core import Configuration, HttpRequest
from azure.core.credentials import AccessToken
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import ContentDecodePolicy, NetworkTraceLoggingPolicy, RetryPolicy
from azure.core.pipeline.transport import HttpTransport, RequestsTransport
from msal import TokenCache

from .exceptions import AuthenticationError

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
        try:
            if "deserialized_data" in response.context:
                payload = response.context["deserialized_data"]
            else:
                payload = response.http_response.text()
            token = payload["access_token"]

            # these values are strings in IMDS responses but msal.TokenCache requires they be integers
            # https://github.com/AzureAD/microsoft-authentication-library-for-python/pull/55
            expires_in = int(payload.get("expires_in", 0))
            if expires_in != 0:
                payload["expires_in"] = expires_in
            if "ext_expires_in" in payload:
                payload["ext_expires_in"] = int(payload["ext_expires_in"])

            # AccessToken contains the token's expires_on time. There are four cases for setting it:
            # 1. response has expires_on -> AccessToken uses it
            # 2. response has expires_on and expires_in -> AccessToken uses expires_on
            # 3. response has only expires_in -> AccessToken uses expires_in + time of request
            # 4. response has neither expires_on nor expires_in -> AccessToken sets expires_on = 0
            #    (not expecting this case; if it occurs, the token is effectively single-use)
            expires_on = payload.get("expires_on", 0)
            if not isinstance(expires_on, int):
                # would test for str but that isn't 2/3 compatible and this should be safe because payload was json
                try:
                    # maybe it's epoch seconds in a string (likely) or a float (doubtful)
                    expires_on = int(expires_on)
                except ValueError:
                    # probably an App Service MSI response then
                    try:
                        t = self._parse_app_service_expires_on(expires_on)
                        expires_on = calendar.timegm(t)
                    except ValueError:
                        # couldn't parse expires_on -> treat the token as single-use
                        expires_on = request_time
                # ensure the cache entry gets epoch seconds as an int for expires_on
                payload["expires_on"] = expires_on

            self._cache.add({"response": payload, "scope": scopes})

            return AccessToken(token, expires_on or expires_in + request_time)
        except KeyError:
            if "access_token" in payload:
                payload["access_token"] = "****"
            raise AuthenticationError("Unexpected authentication response: {}".format(payload))
        except Exception as ex:
            raise AuthenticationError("Authentication failed: {}".format(str(ex)))

    @staticmethod
    def _parse_app_service_expires_on(expires_on):
        # type: (str) -> struct_time
        """
        Parses expires_on from an App Service MSI response (e.g. "06/19/2019 23:42:01 +00:00") to struct_time.
        Expects the time is UTC (i.e. has offset +00:00).
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
    """Synchronous authentication client"""

    def __init__(self, auth_url, config=None, policies=None, transport=None, **kwargs):
        # type: (str, Optional[Configuration], Optional[Iterable[HTTPPolicy]], Optional[HttpTransport], Mapping[str, Any]) -> None
        config = config or self.create_config(**kwargs)
        policies = policies or [ContentDecodePolicy(), config.logging_policy, config.retry_policy]
        if not transport:
            transport = RequestsTransport(configuration=config)
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
