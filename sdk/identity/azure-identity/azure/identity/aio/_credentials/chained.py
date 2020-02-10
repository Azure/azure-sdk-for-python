# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError
from .base import AsyncCredentialBase
from ... import CredentialUnavailableError
from ..._credentials.chained import _get_error_message

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import AccessToken
    from azure.core.credentials_async import AsyncTokenCredential


class ChainedTokenCredential(AsyncCredentialBase):
    """A sequence of credentials that is itself a credential.

    Its :func:`get_token` method calls ``get_token`` on each credential in the sequence, in order, returning the first
    valid token received.

    :param credentials: credential instances to form the chain
    :type credentials: :class:`azure.core.credentials.AsyncTokenCredential`
    """

    def __init__(self, *credentials: "AsyncTokenCredential") -> None:
        if not credentials:
            raise ValueError("at least one credential is required")
        self.credentials = credentials

    async def close(self):
        """Close the transport sessions of all credentials in the chain."""

        await asyncio.gather(*(credential.close() for credential in self.credentials))

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Asynchronously request a token from each credential, in order, returning the first token received.

        If no credential provides a token, raises :class:`azure.core.exceptions.ClientAuthenticationError`
        with an error message from each credential.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the token
        :raises ~azure.core.exceptions.ClientAuthenticationError: no credential in the chain provided a token
        """
        history = []
        for credential in self.credentials:
            try:
                return await credential.get_token(*scopes, **kwargs)
            except CredentialUnavailableError as ex:
                # credential didn't attempt authentication because it lacks required data or state -> continue
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                # credential failed to authenticate, or something unexpectedly raised -> break
                history.append((credential, str(ex)))
                break

        error_message = _get_error_message(history)
        raise ClientAuthenticationError(message=error_message)
