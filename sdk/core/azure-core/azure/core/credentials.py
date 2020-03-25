# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import TYPE_CHECKING
import six


if TYPE_CHECKING:
    from typing import Any, NamedTuple
    from typing_extensions import Protocol

    AccessToken = NamedTuple("AccessToken", [("token", str), ("expires_on", int)])

    class TokenCredential(Protocol):
        """Protocol for classes able to provide OAuth tokens.

        :param str scopes: Lets you specify the type of access needed.
        """

        # pylint:disable=too-few-public-methods
        def get_token(self, *scopes, **kwargs):
            # type: (*str, **Any) -> AccessToken
            pass


else:
    from collections import namedtuple

    AccessToken = namedtuple("AccessToken", ["token", "expires_on"])

__all__ = ["AzureKeyCredential"]


class AzureKeyCredential(object):
    """Credential type used for authenticating to an Azure service.
    It provides the ability to update the key without creating a new client.

    :param str api_key: The API key to your Azure account.
    :raises: TypeError
    """

    def __init__(self, api_key):
        # type: (str) -> None
        if not isinstance(api_key, six.string_types):
            raise TypeError("api_key must be a string.")
        self._api_key = api_key  # type: str

    @property
    def api_key(self):
        # type () -> str
        """The value of the configured API key.

        :rtype: str
        """
        return self._api_key

    def update_key(self, key):
        # type: (str) -> None
        """Update the API key.

        This can be used when you've regenerated your service API key and want
        to update long-lived clients.

        :param str key: The API key to your Azure account.
        :raises: TypeError
        """
        if not key:
            raise TypeError("The API key used for updating can not be None or empty")
        if not isinstance(key, six.string_types):
            raise TypeError("The API key used for updating must be a string.")
        self._api_key = key
