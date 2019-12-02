# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

from msal import TokenCache
from azure.core.configuration import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    AsyncRetryPolicy,
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
)
from azure.core.pipeline.transport import AioHttpTransport

from .._authn_client import AuthnClientBase
from .._constants import KnownAuthorities

if TYPE_CHECKING:
    from typing import Any, Dict, Iterable, Mapping, Optional
    from azure.core.pipeline.policies import HTTPPolicy
    from azure.core.pipeline.transport import AsyncHttpTransport


class AsyncAuthnClient(AuthnClientBase):  # pylint:disable=async-client-bad-name
    """Async authentication client"""

    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(
        self,
        config: "Optional[Configuration]" = None,
        policies: "Optional[Iterable[HTTPPolicy]]" = None,
        transport: "Optional[AsyncHttpTransport]" = None,
        **kwargs: "Any"
    ) -> None:
        config = config or self._create_config(**kwargs)
        policies = policies or [
            ContentDecodePolicy(),
            config.proxy_policy,
            config.retry_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        if not transport:
            transport = AioHttpTransport(**kwargs)
        self._pipeline = AsyncPipeline(transport=transport, policies=policies)
        super().__init__(**kwargs)

    async def request_token(
        self,
        scopes: "Iterable[str]",
        method: "Optional[str]" = "POST",
        headers: "Optional[Mapping[str, str]]" = None,
        form_data: "Optional[Mapping[str, str]]" = None,
        params: "Optional[Dict[str, str]]" = None,
        **kwargs: "Any"
    ) -> AccessToken:
        request = self._prepare_request(method, headers=headers, form_data=form_data, params=params)
        request_time = int(time.time())
        response = await self._pipeline.run(request, stream=False, **kwargs)
        token = self._deserialize_and_cache_token(response=response, scopes=scopes, request_time=request_time)
        return token

    async def obtain_token_by_refresh_token(
        self, scopes: "Iterable[str]", username: "Optional[str]" = None
    ) -> "AccessToken":
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
                    "This is not currently supported by SharedTokenCacheCredential"
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
                response = await self._pipeline.run(request, stream=False)
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
    def _create_config(**kwargs: "Any") -> Configuration:
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = AsyncRetryPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        return config
