# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import os
import sys


from msal import TokenCache
from azure.core.exceptions import ClientAuthenticationError
from .._constants import KnownAuthorities

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
    from typing import Any, Iterable, List, Mapping, Optional
    import msal_extensions
    from azure.core.credentials import AccessToken
    from .._internal import AadClientBase

    CacheItem = Mapping[str, str]


MULTIPLE_ACCOUNTS = """Multiple users were discovered in the shared token cache. If using DefaultAzureCredential, set
the AZURE_USERNAME environment variable to the preferred username. Otherwise,
specify it when constructing SharedTokenCacheCredential.
Discovered accounts: {}"""

MULTIPLE_MATCHING_ACCOUNTS = """Found multiple accounts matching{}{}. If using DefaultAzureCredential, set environment
variables AZURE_USERNAME and AZURE_TENANT_ID with the preferred username and tenant.
Otherwise, specify them when constructing SharedTokenCacheCredential.
Discovered accounts: {}"""

NO_ACCOUNTS = """The shared cache contains no signed-in accounts. To authenticate with SharedTokenCacheCredential, login
through developer tooling supporting Azure single sign on"""

NO_MATCHING_ACCOUNTS = """The cache contains no account matching the specified{}{}. To authenticate with
SharedTokenCacheCredential, login through developer tooling supporting Azure single sign on.
Discovered accounts: {}"""

NO_TOKEN = """Token acquisition failed for user '{}'. To fix, re-authenticate
through developer tooling supporting Azure single sign on"""

# build a dictionary {authority: {its known aliases}}, aliases taken from MSAL.NET's KnownMetadataProvider
KNOWN_ALIASES = {
    alias: aliases  # N.B. aliases includes alias itself
    for aliases in (
        frozenset((KnownAuthorities.AZURE_CHINA, "login.partner.microsoftonline.cn")),
        frozenset((KnownAuthorities.AZURE_PUBLIC_CLOUD, "login.windows.net", "login.microsoft.com", "sts.windows.net")),
        frozenset((KnownAuthorities.AZURE_GOVERNMENT, "login.usgovcloudapi.net")),
    )
    for alias in aliases
}


def _account_to_string(account):
    username = account.get("username")
    home_account_id = account.get("home_account_id", "").split(".")
    tenant_id = home_account_id[-1] if len(home_account_id) == 2 else ""
    return "(username: {}, tenant: {})".format(username, tenant_id)


def _filtered_accounts(accounts, username=None, tenant_id=None):
    """yield accounts matching username and/or tenant_id"""

    filtered_accounts = []
    for account in accounts:
        if username and account.get("username") != username:
            continue
        if tenant_id:
            try:
                _, tenant = account["home_account_id"].split(".")
                if tenant_id != tenant:
                    continue
            except Exception:  # pylint:disable=broad-except
                continue
        filtered_accounts.append(account)
    return filtered_accounts


class SharedTokenCacheBase(ABC):
    def __init__(self, username=None, **kwargs):  # pylint:disable=unused-argument
        # type: (Optional[str], **Any) -> None

        self._authority = kwargs.pop("authority", None) or KnownAuthorities.AZURE_PUBLIC_CLOUD
        self._authority_aliases = KNOWN_ALIASES.get(self._authority) or frozenset((self._authority,))
        self._username = username
        self._tenant_id = kwargs.pop("tenant_id", None)

        cache = kwargs.pop("_cache", None)  # for ease of testing

        if not cache and sys.platform.startswith("win") and "LOCALAPPDATA" in os.environ:
            from msal_extensions.token_cache import WindowsTokenCache

            cache = WindowsTokenCache(
                cache_location=os.path.join(os.environ["LOCALAPPDATA"], ".IdentityService", "msal.cache")
            )

            # prevent writing to the shared cache
            # TODO: seperating deserializing access tokens from caching them would make this cleaner
            cache.add = lambda *_, **__: None

        if cache:
            self._cache = cache
            self._client = self._get_auth_client(
                authority=self._authority, cache=cache, **kwargs
            )  # type: Optional[AadClientBase]
        else:
            self._client = None

    @abc.abstractmethod
    def _get_auth_client(self, **kwargs):
        # type: (**Any) -> AadClientBase
        pass

    def _get_cache_items_for_authority(self, credential_type):
        # type: (TokenCache.CredentialType) -> List[CacheItem]
        """yield cache items matching this credential's authority or one of its aliases"""

        items = []
        for item in self._cache.find(credential_type):
            environment = item.get("environment")
            if environment in self._authority_aliases:
                items.append(item)
        return items

    def _get_accounts_having_matching_refresh_tokens(self):
        # type: () -> Iterable[CacheItem]
        """returns an iterable of cached accounts which have a matching refresh token"""

        refresh_tokens = self._get_cache_items_for_authority(TokenCache.CredentialType.REFRESH_TOKEN)
        all_accounts = self._get_cache_items_for_authority(TokenCache.CredentialType.ACCOUNT)

        accounts = {}
        for refresh_token in refresh_tokens:
            home_account_id = refresh_token.get("home_account_id")
            if not home_account_id:
                continue
            for account in all_accounts:
                # When the token has no family, msal.net falls back to matching client_id,
                # which won't work for the shared cache because we don't know the IDs of
                # all contributing apps. It should be unnecessary anyway because the
                # apps should all belong to the family.
                if home_account_id == account.get("home_account_id") and "family_id" in refresh_token:
                    accounts[account["home_account_id"]] = account
        return accounts.values()

    def _get_account(self, username=None, tenant_id=None):
        # type: (Optional[str], Optional[str]) -> CacheItem
        """returns exactly one account which has a refresh token and matches username and/or tenant_id"""

        accounts = self._get_accounts_having_matching_refresh_tokens()
        if not accounts:
            # cache is empty or contains no refresh token -> user needs to sign in
            raise ClientAuthenticationError(message=NO_ACCOUNTS)

        filtered_accounts = _filtered_accounts(accounts, username, tenant_id)
        if len(filtered_accounts) == 1:
            return filtered_accounts[0]

        # no, or multiple, accounts after filtering -> choose the best error message
        cached_accounts = ", ".join(_account_to_string(account) for account in accounts)
        if username or tenant_id:
            username_string = " username: {}".format(username) if username else ""
            tenant_string = " tenant: {}".format(tenant_id) if tenant_id else ""
            if filtered_accounts:
                message = MULTIPLE_MATCHING_ACCOUNTS.format(username_string, tenant_string, cached_accounts)
            else:
                message = NO_MATCHING_ACCOUNTS.format(username_string, tenant_string, cached_accounts)
        else:
            message = MULTIPLE_ACCOUNTS.format(cached_accounts)

        raise ClientAuthenticationError(message=message)

    def _get_refresh_tokens(self, account):
        return self._cache.find(
            TokenCache.CredentialType.REFRESH_TOKEN, query={"home_account_id": account.get("home_account_id")}
        )

    @staticmethod
    def supported():
        # type: () -> bool
        """Whether the shared token cache is supported on the current platform.

        :rtype: bool
        """
        return sys.platform.startswith("win")
