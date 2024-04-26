# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import abc
from typing import Any, Optional, cast

from .._exceptions import CredentialUnavailableError
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.managed_identity_client import ManagedIdentityClient


class ManagedIdentityBase(GetTokenMixin):
    """Base class for internal credentials using ManagedIdentityClient."""

    from azure.core.credentials import AccessToken

    def __init__(self, **kwargs: Any):
        super(ManagedIdentityBase, self).__init__()
        self._client = self.get_client(**kwargs)

    @abc.abstractmethod
    def get_client(self, **kwargs: Any) -> Optional[ManagedIdentityClient]:
        pass

    @abc.abstractmethod
    def get_unavailable_message(self) -> str:
        pass

    def __enter__(self) -> "ManagedIdentityBase":
        if self._client:
            self._client.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._client:
            self._client.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        if not self._client:
            raise CredentialUnavailableError(message=self.get_unavailable_message())
        return super(ManagedIdentityBase, self).get_token(*scopes, **kwargs)

    def _acquire_token_silently(self, *scopes: str, **kwargs: Any) -> Optional[AccessToken]:
        # casting because mypy can't determine that these methods are called
        # only by get_token, which raises when self._client is None
        return cast(ManagedIdentityClient, self._client).get_cached_token(*scopes)

    def _request_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        return cast(ManagedIdentityClient, self._client).request_token(*scopes, **kwargs)
