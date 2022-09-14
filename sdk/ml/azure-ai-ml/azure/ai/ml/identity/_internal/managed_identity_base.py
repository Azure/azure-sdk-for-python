# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import abc
from typing import TYPE_CHECKING, cast

from azure.identity import CredentialUnavailableError

from .._internal.get_token_mixin import GetTokenMixin
from .._internal.managed_identity_client import ManagedIdentityClient

if TYPE_CHECKING:
    from azure.core.credentials import AccessToken


class ManagedIdentityBase(GetTokenMixin):
    """Base class for internal credentials using ManagedIdentityClient."""

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        super(ManagedIdentityBase, self).__init__()
        self._client = self.get_client(**kwargs)

    @abc.abstractmethod
    def get_client(self, **kwargs):
        # type: (**Any) -> Optional[ManagedIdentityClient]
        pass

    @abc.abstractmethod
    def get_unavailable_message(self):
        # type: () -> str
        pass

    def __enter__(self):
        if self._client:
            self._client.__enter__()
        return self

    def __exit__(self, *args):
        if self._client:
            self._client.__exit__(*args)

    def close(self):
        # type: () -> None
        self.__exit__()

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        if not self._client:
            raise CredentialUnavailableError(message=self.get_unavailable_message())
        return super(ManagedIdentityBase, self).get_token(*scopes, **kwargs)

    def _acquire_token_silently(self, *scopes, **kwargs):
        # type: (*str, **Any) -> Optional[AccessToken]
        # casting because mypy can't determine that these methods are called
        # only by get_token, which raises when self._client is None
        return cast(ManagedIdentityClient, self._client).get_cached_token(*scopes)

    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        return cast(ManagedIdentityClient, self._client).request_token(*scopes, **kwargs)
