# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError
from ... import ChainedTokenCredential as SyncChainedTokenCredential

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import AccessToken


class ChainedTokenCredential(SyncChainedTokenCredential):
    """A sequence of credentials that is itself a credential.

    Its ``get_token`` method calls ``get_token`` on each credential in the sequence, in order, returning the first
    valid token received.

    :param credentials: credential instances to form the chain
    :type credentials: :class:`azure.core.credentials.TokenCredential`
    """

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """Asynchronously request a token from each credential, in order, returning the first token received.

        If no credential provides a token, raises :class:`azure.core.exceptions.ClientAuthenticationError`
        with an error message from each credential.

        :param str scopes: desired scopes for the token
        :raises ~azure.core.exceptions.ClientAuthenticationError:
        """
        history = []
        for credential in self.credentials:
            try:
                return await credential.get_token(*scopes, **kwargs)
            except ClientAuthenticationError as ex:
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                history.append((credential, str(ex)))
        error_message = self._get_error_message(history)
        raise ClientAuthenticationError(message=error_message)
