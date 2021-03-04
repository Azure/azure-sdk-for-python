# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional


class CredentialUnavailableError(ClientAuthenticationError):
    """The credential did not attempt to authenticate because required data or state is unavailable."""


class AuthenticationRequiredError(CredentialUnavailableError):
    """Interactive authentication is required to acquire a token.

    This error is raised only by interactive user credentials configured not to automatically prompt for user
    interaction as needed. Its properties provide additional information that may be required to authenticate. The
    control_interactive_prompts sample demonstrates handling this error by calling a credential's "authenticate"
    method.
    """

    def __init__(self, scopes, message=None, error_details=None, claims=None, **kwargs):
        # type: (Iterable[str], Optional[str], Optional[str], Optional[str], **Any) -> None
        self._claims = claims
        self._scopes = scopes
        self._error_details = error_details
        if not message:
            message = "Interactive authentication is required to get a token. Call 'authenticate' to begin."
        super(AuthenticationRequiredError, self).__init__(message=message, **kwargs)

    @property
    def scopes(self):
        # type: () -> Iterable[str]
        """Scopes requested during the failed authentication"""
        return self._scopes

    @property
    def error_details(self):
        # type: () -> Optional[str]
        """Additional authentication error details from Azure Active Directory"""
        return self._error_details

    @property
    def claims(self):
        # type: () -> Optional[str]
        """Additional claims required in the next authentication"""
        return self._claims
