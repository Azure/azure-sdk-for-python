# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import Any, Optional, Union
from typing_extensions import Protocol, runtime_checkable
from .credentials import AccessToken as _AccessToken


@runtime_checkable
class AsyncTokenCredential(Protocol):
    """Protocol for classes able to provide OAuth tokens."""

    async def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs: Any
    ) -> _AccessToken:
        """Request an access token for `scopes`.

        :param str scopes: The type of access needed.

        :keyword str claims: Additional claims required in the token, such as those returned in a resource
            provider's claims challenge following an authorization failure.
        :keyword str tenant_id: Optional tenant to include in the token request.

        :rtype: AccessToken
        :return: An AccessToken instance containing the token string and its expiration time in Unix time.
        """

    async def close(self) -> None:
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass


class AsyncStaticTokenCredential:
    """Authenticates with a previously acquired access token
    Note that an access token is valid only for certain resources and eventually expires. This credential is therefore
    quite limited. An application using it must ensure the token is valid and contains all claims required by any
    service client given an instance of this credential.

    :param access_token: The pre-acquired access token.
    :type access_token: str or ~azure.core.credentials.AccessToken
    :keyword int expire_in: The number of seconds the token is valid. Defaults to 86400 seconds (1 day).
        Only used if access_token is a str.
    """
    def __init__(self, access_token: Union[str, _AccessToken], *, expire_in: int = 86400) -> None:
        if isinstance(access_token, _AccessToken):
            self._token = access_token
        else:
            self._token = _AccessToken(token=access_token, expires_on=int(time.time()+expire_in))

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def get_token(self, *scopes: str, **kwargs: Any) -> _AccessToken:    # pylint:disable=unused-argument
        """get_token is the only method a credential must implement"""

        return self._token
