# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import calendar
import time

from msal import TokenCache

from azure.core import Configuration, HttpRequest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import ContentDecodePolicy, NetworkTraceLoggingPolicy, ProxyPolicy, RetryPolicy
from azure.core.pipeline.policies.distributed_tracing import DistributedTracingPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.identity._constants import AZURE_CLI_CLIENT_ID

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from time import struct_time
    from typing import Any, Dict, Iterable, Mapping, Optional, Union
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy


class AuthnClientBase(ABC):
    """Sans I/O authentication client methods"""

    def __init__(self, auth_url, **kwargs):  # pylint:disable=unused-argument
        # type: (str, **Any) -> None
        if not auth_url:
            raise ValueError("auth_url should be the URL of an OAuth endpoint")
        super(AuthnClientBase, self).__init__()
        self._auth_url = auth_url
        self._cache = kwargs.get("cache") or TokenCache()  # type: TokenCache

    def get_cached_token(self, scopes):
        # type: (Iterable[str]) -> Optional[AccessToken]
        tokens = self._cache.find(TokenCache.CredentialType.ACCESS_TOKEN, target=list(scopes))
        for token in tokens:
            expires_on = int(token["expires_on"])
            if expires_on - 300 > int(time.time()):
                return AccessToken(token["secret"], expires_on)
        return None

    def get_refresh_tokens(self, scopes, account):
        """Yields all an account's cached refresh tokens except those which have a scope (which is unexpected) that
        isn't a superset of ``scopes``."""

        for token in self._cache.find(
            TokenCache.CredentialType.REFRESH_TOKEN, query={"home_account_id": account.get("home_account_id")}
        ):
            if "target" in token and not all((scope in token["target"] for scope in scopes)):
                continue
            yield token

    def get_refresh_token_grant_request(self, refresh_token, scopes):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token["secret"],
            "scope": " ".join(scopes),
            "client_id": AZURE_CLI_CLIENT_ID,  # TODO: first-party app for SDK?
        }
        return self._prepare_request(form_data=data)

    @abc.abstractmethod
    def request_token(self, scopes, method, headers, form_data, params, **kwargs):
        pass

    @abc.abstractmethod
    def obtain_token_by_refresh_token(self, scopes, username):
        pass

    def _deserialize_and_cache_token(self, response, scopes, request_time):
        # type: (PipelineResponse, Iterable[str], int) -> AccessToken
        """Deserialize and cache an access token from an AAD response"""

        # ContentDecodePolicy sets this, and should have raised if it couldn't deserialize the response
        payload = response.context[ContentDecodePolicy.CONTEXT_NAME]

        if not payload or "access_token" not in payload or not ("expires_in" in payload or "expires_on" in payload):
            if payload and "access_token" in payload:
                payload["access_token"] = "****"
            raise ClientAuthenticationError(message="Unexpected response '{}'".format(payload))

        token = payload["access_token"]

        # AccessToken wants expires_on as an int
        expires_on = payload.get("expires_on") or int(payload["expires_in"]) + request_time  # type: Union[str, int]
        try:
            expires_on = int(expires_on)
        except ValueError:
            # probably an App Service MSI response, convert it to epoch seconds
            try:
                t = self._parse_app_service_expires_on(expires_on)  # type: ignore
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
    def _prepare_request(
        self,
        method="POST",  # type: Optional[str]
        headers=None,  # type: Optional[Mapping[str, str]]
        form_data=None,  # type: Optional[Mapping[str, str]]
        params=None,  # type: Optional[Dict[str, str]]
    ):
        # type: (...) -> HttpRequest
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

    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(
        self,
        auth_url,  # type: str
        config=None,  # type: Optional[Configuration]
        policies=None,  # type: Optional[Iterable[HTTPPolicy]]
        transport=None,  # type: Optional[HttpTransport]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        config = config or self._create_config(**kwargs)
        policies = policies or [
            ContentDecodePolicy(),
            config.retry_policy,
            config.logging_policy,
            DistributedTracingPolicy(),
        ]
        if not transport:
            transport = RequestsTransport(**kwargs)
        self._pipeline = Pipeline(transport=transport, policies=policies)
        super(AuthnClient, self).__init__(auth_url, **kwargs)

    def request_token(
        self,
        scopes,  # type: Iterable[str]
        method="POST",  # type: Optional[str]
        headers=None,  # type: Optional[Mapping[str, str]]
        form_data=None,  # type: Optional[Mapping[str, str]]
        params=None,  # type: Optional[Dict[str, str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> AccessToken
        request = self._prepare_request(method, headers=headers, form_data=form_data, params=params)
        request_time = int(time.time())
        response = self._pipeline.run(request, stream=False, **kwargs)
        token = self._deserialize_and_cache_token(response=response, scopes=scopes, request_time=request_time)
        return token

    def obtain_token_by_refresh_token(self, scopes, username):
        # type: (Iterable[str], str) -> Optional[AccessToken]
        """Acquire an access token using a cached refresh token. Returns ``None`` when that fails, or the cache has no
        refresh token. This is only used by SharedTokenCacheCredential and isn't robust enough for anything else."""

        # find account matching username
        accounts = self._cache.find(TokenCache.CredentialType.ACCOUNT, query={"username": username})
        for account in accounts:
            # try each refresh token that might work, return the first access token acquired
            for token in self.get_refresh_tokens(scopes, account):
                # currently we only support login.microsoftonline.com, which has an alias login.windows.net
                # TODO: this must change to support sovereign clouds
                environment = account.get("environment")
                if not environment or (environment not in self._auth_url and environment != "login.windows.net"):
                    continue

                request = self.get_refresh_token_grant_request(token, scopes)
                request_time = int(time.time())
                response = self._pipeline.run(request, stream=False)
                try:
                    return self._deserialize_and_cache_token(
                        response=response, scopes=scopes, request_time=request_time
                    )
                except ClientAuthenticationError:
                    continue

        return None

    @staticmethod
    def _create_config(**kwargs):
        # type: (Mapping[str, Any]) -> Configuration
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        return config
