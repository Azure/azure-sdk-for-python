# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from collections import namedtuple
from typing import Any, NamedTuple, Optional
from typing_extensions import Protocol, runtime_checkable


class AccessToken(NamedTuple):
    """Represents an OAuth access token."""

    token: str
    expires_on: int


AccessToken.token.__doc__ = """The token string."""
AccessToken.expires_on.__doc__ = """The token's expiration time in Unix time."""


@runtime_checkable
class TokenCredential(Protocol):
    """Protocol for classes able to provide OAuth tokens."""

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs: Any
    ) -> AccessToken:
        """Request an access token for `scopes`.

        :param str scopes: The type of access needed.

        :keyword str claims: Additional claims required in the token, such as those returned in a resource
            provider's claims challenge following an authorization failure.
        :keyword str tenant_id: Optional tenant to include in the token request.

        :rtype: AccessToken
        :return: An AccessToken instance containing the token string and its expiration time in Unix time.
        """


AzureNamedKey = namedtuple("AzureNamedKey", ["name", "key"])


__all__ = [
    "AzureKeyCredential",
    "AzureSasCredential",
    "AccessToken",
    "AzureNamedKeyCredential",
    "AzureDuoKeyCredential",
    "TokenCredential",
]


class AzureKeyCredential:
    """Credential type used for authenticating to an Azure service.
    It provides the ability to update the key without creating a new client.

    :param str key: The key used to authenticate to an Azure service
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
        """
        return self._key

    def update(self, key: str) -> None:
        """Update the key.

        This can be used when you've regenerated your service key and want
        to update long-lived clients.

        :param str key: The key used to authenticate to an Azure service
        :raises: ValueError or TypeError
        """
        if not key:
            raise ValueError("The key used for updating can not be None or empty")
        if not isinstance(key, str):
            raise TypeError("The key used for updating must be a string.")
        self._key = key


class AzureDuoKeyCredential:
    """Credential type used for authenticating to an Azure service.
    It provides the ability to store two keys with custom headers for a client.

    :param str header1: The first header value.
    :param str key1: The first key used to authenticate to an Azure service.
    :param str header2: The second header value.
    :param str key2: The second key used to authenticate to an Azure service.
    """

    def __init__(self, header1: str, key1: str, header2: str, key2: str) -> None:
        self._header1 = header1
        self._key1 = key1
        self._header2 = header2
        self._key2 = key2

    def get_key(self, header: str) -> str:
        """The value of specified header. If header is not found, raise ValueError.

        :param str header: The header of the key to get. It is case-insensitive.
        :rtype: str
        :raises: ValueError
        """
        if self._header1.lower() == header.lower():
            return self._key1
        if self._header2.lower() == header.lower():
            return self._key2
        raise ValueError("The header {} is not found.".format(header))

    @property
    def header1(self) -> str:
        """The value of header1.

        :rtype: str
        """
        return self._header1

    @property
    def header2(self) -> str:
        """The value of header2.

        :rtype: str
        """
        return self._header2

    def _update(self, header: str, key: str) -> None:
        """Update the key with specified header. If header is not found, raise ValueError.

        This can be used when you've regenerated your service key and want
        to update long-lived clients.

        :param str header: The header of the key to update. It is case-insensitive.
        :param str key: The key used to authenticate to an Azure service
        :raises: ValueError
        """
        if self._header1.lower() == header.lower():
            self._key1 = key
            return
        if self._header2.lower() == header.lower():
            self._key2 = key
            return
        raise ValueError("The header {} is not found.".format(header))


class AzureSasCredential:
    """Credential type used for authenticating to an Azure service.
    It provides the ability to update the shared access signature without creating a new client.

    :param str signature: The shared access signature used to authenticate to an Azure service
    :raises: TypeError
    """

    def __init__(self, signature: str) -> None:
        if not isinstance(signature, str):
            raise TypeError("signature must be a string.")
        self._signature = signature

    @property
    def signature(self) -> str:
        """The value of the configured shared access signature.

        :rtype: str
        """
        return self._signature

    def update(self, signature: str) -> None:
        """Update the shared access signature.

        This can be used when you've regenerated your shared access signature and want
        to update long-lived clients.

        :param str signature: The shared access signature used to authenticate to an Azure service
        :raises: ValueError or TypeError
        """
        if not signature:
            raise ValueError("The signature used for updating can not be None or empty")
        if not isinstance(signature, str):
            raise TypeError("The signature used for updating must be a string.")
        self._signature = signature


class AzureNamedKeyCredential:
    """Credential type used for working with any service needing a named key that follows patterns
    established by the other credential types.

    :param str name: The name of the credential used to authenticate to an Azure service.
    :param str key: The key used to authenticate to an Azure service.
    :raises: TypeError
    """

    def __init__(self, name: str, key: str) -> None:
        if not isinstance(name, str) or not isinstance(key, str):
            raise TypeError("Both name and key must be strings.")
        self._credential = AzureNamedKey(name, key)

    @property
    def named_key(self) -> AzureNamedKey:
        """The value of the configured name.

        :rtype: AzureNamedKey
        """
        return self._credential

    def update(self, name: str, key: str) -> None:
        """Update the named key credential.

        Both name and key must be provided in order to update the named key credential.
        Individual attributes cannot be updated.

        :param str name: The name of the credential used to authenticate to an Azure service.
        :param str key: The key used to authenticate to an Azure service.
        """
        if not isinstance(name, str) or not isinstance(key, str):
            raise TypeError("Both name and key must be strings.")
        self._credential = AzureNamedKey(name, key)
