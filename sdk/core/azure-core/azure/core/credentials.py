# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Any, NamedTuple, Optional, Dict
from typing_extensions import Protocol, runtime_checkable


class AccessToken(NamedTuple):
    """Represents an OAuth access token."""

    token: str
    """The token string."""
    expires_on: int
    """The token's expiration time in Unix time."""


class ExtendedAccessToken(AccessToken):
    """Represents an OAuth access token with additional properties.

    Currently, the only additional property is the token's refresh on time.

    In order to maintain backwards compatibility with the base AccessToken, only properties defined
    in the base class are used for operations like comparison and iteration.

    :param str token: The token string.
    :param int expires_on: The token's expiration time in Unix time.
    :keyword int refresh_on: The token's refresh on time in Unix time. Optional.
    """

    _refresh_on: Optional[int]

    def __new__(cls, token: str, expires_on: int, *, refresh_on: Optional[int] = None):
        instance = super().__new__(cls, token, expires_on)
        instance._refresh_on = refresh_on
        return instance

    @property
    def refresh_on(self) -> Optional[int]:
        """The token's refresh on time in Unix time.

        :rtype: Optional[int]
        """
        return self._refresh_on


class ExtensionAccessToken(AccessToken):
    """Exploratory class for storing arbitrary token metadata."""

    _additional_properties: Dict[str, Any]

    def __new__(cls, token: str, expires_on: int, **kwargs: Any):
        instance = super().__new__(cls, token, expires_on)
        instance._additional_properties = kwargs
        return instance

    @property
    def additional_properties(self) -> Dict[str, Any]:
        """The additional properties or metadata of the token.

        :rtype: dict[str, Any]
        """
        return self._additional_properties


@runtime_checkable
class TokenCredential(Protocol):
    """Protocol for classes able to provide OAuth tokens."""

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any
    ) -> AccessToken:
        """Request an access token for `scopes`.

        :param str scopes: The type of access needed.

        :keyword str claims: Additional claims required in the token, such as those returned in a resource
            provider's claims challenge following an authorization failure.
        :keyword str tenant_id: Optional tenant to include in the token request.
        :keyword bool enable_cae: Indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Defaults to False.

        :rtype: AccessToken
        :return: An AccessToken instance containing the token string and its expiration time in Unix time.
        """
        ...


class AzureNamedKey(NamedTuple):
    """Represents a name and key pair."""

    name: str
    key: str


__all__ = [
    "AzureKeyCredential",
    "AzureSasCredential",
    "AccessToken",
    "ExtensionAccessToken",
    "ExtendedAccessToken",
    "AzureNamedKeyCredential",
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
        :return: The value of the configured key.
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
        :return: The value of the configured shared access signature.
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
        :return: The value of the configured name.
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
