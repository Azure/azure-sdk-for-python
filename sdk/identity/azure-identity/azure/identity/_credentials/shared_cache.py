# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import os
import sys

from msal import TokenCache

from azure.core.exceptions import ClientAuthenticationError
from .._constants import AZURE_CLI_CLIENT_ID, KnownAuthorities
from .._internal import AadClient, wrap_exceptions


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
    from typing import Any, Mapping, Optional
    import msal_extensions
    from azure.core.credentials import AccessToken
    from .._internal import AadClientBase


MULTIPLE_ACCOUNTS = """Multiple users were discovered in the shared token cache. If using DefaultAzureCredential, set
the AZURE_USERNAME environment variable to the preferred username. Otherwise,
specify it when constructing SharedTokenCacheCredential.\nDiscovered accounts: {}"""

MULTIPLE_MATCHING_ACCOUNTS = """Found multiple accounts matching{}{}. If using DefaultAzureCredential, set environment
variables AZURE_USERNAME and AZURE_TENANT_ID with the preferred username and tenant.
Otherwise, specify them when constructing SharedTokenCacheCredential.\nDiscovered accounts: {}"""

NO_ACCOUNTS = """The shared cache contains no accounts. To authenticate with SharedTokenCacheCredential, login through
developer tooling supporting Azure single sign on"""

NO_MATCHING_ACCOUNTS = """The cache contains no account matching the specified{}{}. To authenticate with
SharedTokenCacheCredential, login through developer tooling supporting Azure single sign on.\nDiscovered accounts: {}"""

NO_TOKEN = """Token acquisition failed for user '{}'. To fix, re-authenticate
through developer tooling supporting Azure single sign on"""


class SharedTokenCacheBase(ABC):
    def __init__(self, username=None, **kwargs):  # pylint:disable=unused-argument
        # type: (Optional[str], **Any) -> None

        self._authority = kwargs.pop("authority", KnownAuthorities.AZURE_PUBLIC_CLOUD)
        self._username = username
        self._tenant_id = kwargs.pop("tenant_id", None)

        cache = kwargs.pop("_cache", None)  # for ease of testing

        if not cache and sys.platform.startswith("win") and "LOCALAPPDATA" in os.environ:
            from msal_extensions.token_cache import WindowsTokenCache

            cache = WindowsTokenCache(cache_location=os.environ["LOCALAPPDATA"] + "/.IdentityService/msal.cache")

            # prevent writing to the shared cache
            # TODO: seperating deserializing access tokens from caching them would make this cleaner
            cache.add = lambda *_: None

        if cache:
            self._cache = cache
            self._client = self._get_auth_client(cache=cache, **kwargs)  # type: Optional[AadClientBase]
        else:
            self._client = None

    @abc.abstractmethod
    def _get_auth_client(self, **kwargs):
        # type: (**Any) -> AadClientBase
        pass

    def _get_account(self, username=None, tenant_id=None):
        # type: (Optional[str], Optional[str]) -> Mapping[str, str]
        accounts = self._cache.find(TokenCache.CredentialType.ACCOUNT)
        if not accounts:
            raise ClientAuthenticationError(message=NO_ACCOUNTS)

        # filter according to arguments
        query = {"username": username} if username else {}
        filtered_accounts = self._cache.find(TokenCache.CredentialType.ACCOUNT, query=query)
        if tenant_id:
            filtered_accounts = [a for a in filtered_accounts if a.get("home_account_id", "").endswith(tenant_id)]

        if len(filtered_accounts) == 1:
            account = filtered_accounts[0]
            environment = account.get("environment")
            if not environment or environment not in self._authority:
                # doubtful this account can get the access token we want but public cloud's a special case
                # because its authority has an alias: for our purposes login.windows.net = login.microsoftonline.com
                if not (environment == "login.windows.net" and self._authority == KnownAuthorities.AZURE_PUBLIC_CLOUD):
                    raise ClientAuthenticationError(message="No token for {}".format(self._authority))
            return account

        cached_accounts = ", ".join(_account_to_string(account) for account in accounts)

        if username or tenant_id:
            # no, or multiple, matching accounts for the given username and/or tenant id
            username_string = " username: {}".format(username) if username else ""
            tenant_string = " tenant: {}".format(tenant_id) if tenant_id else ""
            if not filtered_accounts:
                message = NO_MATCHING_ACCOUNTS.format(username_string, tenant_string, cached_accounts)
            else:
                message = MULTIPLE_MATCHING_ACCOUNTS.format(username_string, tenant_string, cached_accounts)
            raise ClientAuthenticationError(message=message)

        # multiple cached accounts and no basis for selection
        raise ClientAuthenticationError(message=MULTIPLE_ACCOUNTS.format(cached_accounts))

    def _get_refresh_tokens(self, scopes, account):
        """Yields all an account's cached refresh tokens except those which have a scope (which is unexpected) that
        isn't a superset of ``scopes``."""

        for token in self._cache.find(
            TokenCache.CredentialType.REFRESH_TOKEN, query={"home_account_id": account.get("home_account_id")}
        ):
            if "target" in token and not all((scope in token["target"] for scope in scopes)):
                continue
            yield token

    @staticmethod
    def supported():
        # type: () -> bool
        """Whether the shared token cache is supported on the current platform.

        :rtype: bool
        """
        return sys.platform.startswith("win")


class SharedTokenCacheCredential(SharedTokenCacheBase):
    """Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username:
        Username (typically an email address) of the user to authenticate as. This is used when the local cache
        contains tokens for multiple identities.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
        defines authorities for other clouds.
    :keyword str tenant_id: an Azure Active Directory tenant ID. Used to select an account when the cache contains
        tokens for multiple identities.
    """

    @wrap_exceptions
    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type (*str, **Any) -> AccessToken
        """Get an access token for `scopes` from the shared cache.

        If no access token is cached, attempt to acquire one using a cached refresh token.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises:
            :class:`azure.core.exceptions.ClientAuthenticationError` when the cache is unavailable or no access token
            can be acquired from it
        """

        if not self._client:
            raise ClientAuthenticationError(message="Shared token cache unavailable")

        account = self._get_account(self._username, self._tenant_id)

        # try each refresh token, returning the first access token acquired
        for refresh_token in self._get_refresh_tokens(scopes, account):
            token = self._client.obtain_token_by_refresh_token(refresh_token, scopes)
            return token

        raise ClientAuthenticationError(message=NO_TOKEN.format(account.get("username")))

    def _get_auth_client(self, **kwargs):
        # type: (**Any) -> AadClientBase
        return AadClient(tenant_id="common", client_id=AZURE_CLI_CLIENT_ID, **kwargs)


def _account_to_string(account):
    username = account.get("username")
    home_account_id = account.get("home_account_id", "").split(".")
    tenant_id = home_account_id[-1] if len(home_account_id) == 2 else ""
    return "(username: {}, tenant: {})".format(username, tenant_id)
