# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from __future__ import annotations
from types import TracebackType
from typing import NamedTuple, Optional, AsyncContextManager, Type, TypedDict, ContextManager
from typing_extensions import Protocol, runtime_checkable


class AccessTokenInfo:
    """Information about an OAuth access token.

    :param str token: The token string.
    :param int expires_on: The token's expiration time in Unix time.
    :keyword str token_type: The type of access token. Defaults to 'Bearer'.
    :keyword int refresh_on: Specifies the time, in Unix time, when the cached token should be proactively
        refreshed. Optional.
    """

    token: str
    """The token string."""
    expires_on: int
    """The token's expiration time in Unix time."""
    token_type: str
    """The type of access token."""
    refresh_on: Optional[int]
    """Specifies the time, in Unix time, when the cached token should be proactively refreshed. Optional."""

    def __init__(
        self, token: str, expires_on: int, *, token_type: str = "Bearer", refresh_on: Optional[int] = None
    ) -> None:
        self.token = token
        self.expires_on = expires_on
        self.token_type = token_type
        self.refresh_on = refresh_on

    def __repr__(self) -> str:
        return "AccessTokenInfo(token='{}', expires_on={}, token_type='{}', refresh_on={})".format(
            self.token, self.expires_on, self.token_type, self.refresh_on
        )


class TokenRequestOptions(TypedDict, total=False):
    """Options to use for access token requests. All parameters are optional."""

    claims: str
    """Additional claims required in the token, such as those returned in a resource provider's claims
    challenge following an authorization failure."""
    tenant_id: str
    """The tenant ID to include in the token request."""


class TokenCredential(Protocol, ContextManager["TokenCredential"]):
    """Protocol for classes able to provide OAuth access tokens."""

    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes`.

        :param str scopes: The type of access needed.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: TokenRequestOptions

        :rtype: AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.
        """
        ...

    def close(self) -> None:
        pass


class ServiceNamedKey(NamedTuple):
    """Represents a name and key pair."""

    name: str
    key: str


__all__ = [
    "AccessTokenInfo",
    "ServiceKeyCredential",
    "ServiceNamedKeyCredential",
    "TokenCredential",
    "TokenRequestOptions",
    "AsyncTokenCredential",
]


class ServiceKeyCredential:
    """Credential type used for authenticating to a service.
    It provides the ability to update the key without creating a new client.

    :param str key: The key used to authenticate to a service
    :raises: TypeError
    """

    def __init__(self, key: str) -> None:
        if not isinstance(key, str):
            raise TypeError("key must be a string.")
        self._key = key

    @property
    def key(self) -> str:
        """The value of the configured key.

        :rtype: str
        :return: The value of the configured key.
        """
        return self._key

    def update(self, key: str) -> None:
        """Update the key.

        This can be used when you've regenerated your service key and want
        to update long-lived clients.

        :param str key: The key used to authenticate to a service
        :raises: ValueError or TypeError
        """
        if not key:
            raise ValueError("The key used for updating can not be None or empty")
        if not isinstance(key, str):
            raise TypeError("The key used for updating must be a string.")
        self._key = key


class ServiceNamedKeyCredential:
    """Credential type used for working with any service needing a named key that follows patterns
    established by the other credential types.

    :param str name: The name of the credential used to authenticate to a service.
    :param str key: The key used to authenticate to a service.
    :raises: TypeError
    """

    def __init__(self, name: str, key: str) -> None:
        if not isinstance(name, str) or not isinstance(key, str):
            raise TypeError("Both name and key must be strings.")
        self._credential = ServiceNamedKey(name, key)

    @property
    def named_key(self) -> ServiceNamedKey:
        """The value of the configured name.

        :rtype: ServiceNamedKey
        :return: The value of the configured name.
        """
        return self._credential

    def update(self, name: str, key: str) -> None:
        """Update the named key credential.

        Both name and key must be provided in order to update the named key credential.
        Individual attributes cannot be updated.

        :param str name: The name of the credential used to authenticate to a service.
        :param str key: The key used to authenticate to a service.
        """
        if not isinstance(name, str) or not isinstance(key, str):
            raise TypeError("Both name and key must be strings.")
        self._credential = ServiceNamedKey(name, key)


@runtime_checkable
class AsyncTokenCredential(Protocol, AsyncContextManager["AsyncTokenCredential"]):
    """Protocol for classes able to provide OAuth tokens."""

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes`.

        :param str scopes: The type of access needed.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: TokenRequestOptions

        :rtype: AccessTokenInfo
        :return: An AccessTokenInfo instance containing the token string and its expiration time in Unix time.
        """
        ...

    async def close(self) -> None:
        pass

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        pass
