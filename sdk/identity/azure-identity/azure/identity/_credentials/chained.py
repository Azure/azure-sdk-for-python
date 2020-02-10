# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.exceptions import ClientAuthenticationError

from .. import CredentialUnavailableError

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import AccessToken, TokenCredential


def _get_error_message(history):
    attempts = []
    for credential, error in history:
        if error:
            attempts.append("{}: {}".format(credential.__class__.__name__, error))
        else:
            attempts.append(credential.__class__.__name__)
    return """No credential in this chain provided a token.
Attempted credentials:\n\t{}""".format(
        "\n\t".join(attempts)
    )


class ChainedTokenCredential(object):
    """A sequence of credentials that is itself a credential.

    Its :func:`get_token` method calls ``get_token`` on each credential in the sequence, in order, returning the first
    valid token received.

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
        """Request a token from each chained credential, in order, returning the first token received.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the token
        :raises ~azure.core.exceptions.ClientAuthenticationError: no credential in the chain provided a token
        """
        history = []
        for credential in self.credentials:
            try:
                return credential.get_token(*scopes, **kwargs)
            except CredentialUnavailableError as ex:
                # credential didn't attempt authentication because it lacks required data or state -> continue
                history.append((credential, ex.message))
            except Exception as ex:  # pylint: disable=broad-except
                # credential failed to authenticate, or something unexpectedly raised -> break
                history.append((credential, str(ex)))
                break

        error_message = _get_error_message(history)
        raise ClientAuthenticationError(message=error_message)
