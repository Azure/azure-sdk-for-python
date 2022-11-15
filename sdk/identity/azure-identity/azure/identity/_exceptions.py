# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Iterable, Optional

from azure.core.exceptions import ClientAuthenticationError


class CredentialUnavailableError(ClientAuthenticationError):
    """The credential did not attempt to authenticate because required data or state is unavailable."""


class AuthenticationRequiredError(CredentialUnavailableError):
    """Interactive authentication is required to acquire a token.

    This error is raised only by interactive user credentials configured not to automatically prompt for user
    interaction as needed. Its properties provide additional information that may be required to authenticate. The
    control_interactive_prompts sample demonstrates handling this error by calling a credential's "authenticate"
    method.
    """

    def __init__(self, scopes, message=None, claims=None, **kwargs):
        # type: (Iterable[str], Optional[str], Optional[str], **Any) -> None
        self._claims = claims
        self._scopes = scopes
        if not message:
            message = "Interactive authentication is required to get a token. Call 'authenticate' to begin."
        super(AuthenticationRequiredError, self).__init__(message=message, **kwargs)

    @property
    def scopes(self):
        # type: () -> Iterable[str]
        """Scopes requested during the failed authentication"""
        return self._scopes

    @property
    def claims(self):
        # type: () -> Optional[str]
        """Additional claims required in the next authentication"""
        return self._claims
