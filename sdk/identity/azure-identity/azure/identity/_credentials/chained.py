# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ClientAuthenticationError

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import AccessToken, TokenCredential


class ChainedTokenCredential(object):
    """
    A sequence of credentials that is itself a credential. Its ``get_token`` method calls ``get_token`` on each
    credential in the sequence, in order, returning the first valid token received.

    :param credentials: credential instances to form the chain
    :type credentials: :class:`azure.core.credentials.TokenCredential`
    """

    def __init__(self, *credentials):
        # type: (*TokenCredential) -> None
        if not credentials:
            raise ValueError("at least one credential is required")
        self.credentials = credentials

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """
        Request a token from each chained credential, in order, returning the first token received.
        If none provides a token, raises :class:`azure.core.exceptions.ClientAuthenticationError` with an
        error message from each credential.

        :param str scopes: desired scopes for the token
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        history = []
        for credential in self.credentials:
            try:
                return credential.get_token(*scopes, **kwargs)
            except ClientAuthenticationError as ex:
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                history.append((credential, str(ex)))
        error_message = self._get_error_message(history)
        raise ClientAuthenticationError(message=error_message)

    @staticmethod
    def _get_error_message(history):
        attempts = []
        for credential, error in history:
            if error:
                attempts.append("{}: {}".format(credential.__class__.__name__, error))
            else:
                attempts.append(credential.__class__.__name__)
        return "No valid token received. {}".format(". ".join(attempts))
