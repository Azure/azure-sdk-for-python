# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import calendar
import time

from msal import TokenCache

from azure.core.configuration import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    RetryPolicy,
    DistributedTracingPolicy,
)
from azure.core.pipeline.transport import RequestsTransport, HttpRequest
from ._constants import AZURE_CLI_CLIENT_ID, KnownAuthorities

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

    def __init__(self, endpoint=None, authority=None, tenant=None, **kwargs):  # pylint:disable=unused-argument
        # type: (Optional[str], Optional[str], Optional[str], **Any) -> None
        super(AuthnClientBase, self).__init__()
        if authority and endpoint:
            raise ValueError(
                "'authority' and 'endpoint' are mutually exclusive. 'authority' should be the authority of an AAD"
                + " endpoint, whereas 'endpoint' should be the endpoint's full URL."
            )

        if endpoint:
            self._auth_url = endpoint
        else:
            if not tenant:
                raise ValueError("'tenant' is required")
            authority = authority or KnownAuthorities.AZURE_PUBLIC_CLOUD
            self._auth_url = "https://" + "/".join((authority.strip("/"), tenant.strip("/"), "oauth2/v2.0/token"))
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
        # type: (Iterable[str], Optional[str]) -> AccessToken
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
        """Parse expires_on from an App Service MSI response (e.g. "06/19/2019 23:42:01 +00:00") to struct_time.
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
    """Synchronous authentication client.

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
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        if not transport:
            transport = RequestsTransport(**kwargs)
        self._pipeline = Pipeline(transport=transport, policies=policies)
        super(AuthnClient, self).__init__(**kwargs)

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

    def obtain_token_by_refresh_token(self, scopes, username=None):
        # type: (Iterable[str], Optional[str]) -> AccessToken
        """Acquire an access token using a cached refresh token. Raises ClientAuthenticationError if that fails.
        This is only used by SharedTokenCacheCredential and isn't robust enough for anything else."""

        # if an username is provided, restrict our search to accounts that have that username
        query = {"username": username} if username else {}
        accounts = self._cache.find(TokenCache.CredentialType.ACCOUNT, query=query)

        # if more than one account was returned, ensure that that they all have the same home_account_id. If so,
        # we'll treat them as equal, otherwise we can't know which one to pick, so we'll raise an error.
        if len(accounts) > 1 and len({account.get("home_account_id") for account in accounts}) != 1:
            if username:
                message = (
                    "Multiple entries found for user '{}' were found in the shared token cache. "
                    "This is not currently supported by SharedTokenCacheCredential."
                ).format(username)
            else:
                # TODO: we could identify usernames associated with exactly one home account id
                message = (
                    "Multiple users were discovered in the shared token cache. If using DefaultAzureCredential, set "
                    "the AZURE_USERNAME environment variable to the preferred username. Otherwise, specify it when "
                    "constructing SharedTokenCacheCredential."
                    "\nDiscovered accounts: {}"
                ).format(", ".join({account.get("username") for account in accounts}))
            raise ClientAuthenticationError(message=message)

        for account in accounts:
            # ensure the account is associated with the token authority we expect to use
            # ('environment' is an authority e.g. 'login.microsoftonline.com')
            environment = account.get("environment")
            if not environment or environment not in self._auth_url:
                # doubtful this account can get the access token we want but public cloud's a special case
                # because its authority has an alias: for our purposes login.windows.net = login.microsoftonline.com
                if not (environment == "login.windows.net" and KnownAuthorities.AZURE_PUBLIC_CLOUD in self._auth_url):
                    continue

            # try each refresh token, returning the first access token acquired
            for token in self.get_refresh_tokens(scopes, account):
                request = self.get_refresh_token_grant_request(token, scopes)
                request_time = int(time.time())
                response = self._pipeline.run(request, stream=False)
                try:
                    return self._deserialize_and_cache_token(
                        response=response, scopes=scopes, request_time=request_time
                    )
                except ClientAuthenticationError:
                    continue

        message = "No cached token found"
        if username:
            message += " for '{}'".format(username)

        raise ClientAuthenticationError(message=message)

    @staticmethod
    def _create_config(**kwargs):
        # type: (Mapping[str, Any]) -> Configuration
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        return config
