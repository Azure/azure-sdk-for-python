# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from typing import TYPE_CHECKING
from .._exceptions import CredentialUnavailableError
from .._constants import AZURE_VSCODE_CLIENT_ID
from .._internal.aad_client import AadClient

if sys.platform.startswith("win"):
    from .._internal.win_vscode_adapter import get_credentials
elif sys.platform.startswith("darwin"):
    from .._internal.macos_vscode_adapter import get_credentials
else:
    from .._internal.linux_vscode_adapter import get_credentials

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import AccessToken


class VSCodeCredential(object):
    """Authenticates by redeeming a refresh token previously saved by VS Code

    :keyword int token_refresh_retry_timeout: the number of seconds to wait before retrying a token refresh in seconds,
          default to 30s.
    :keyword int token_refresh_offset: the number of seconds to subtract from the token expiry time, whereupon
          attempts will be made to refresh the token. By default this will occur two minutes prior to the expiry
          of the token.

    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._client = kwargs.pop("_client", None) or AadClient("organizations", AZURE_VSCODE_CLIENT_ID, **kwargs)
        self._refresh_token = None

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        When this method is called, the credential will try to get the refresh token saved by VS Code. If a refresh
        token can be found, it will redeem the refresh token for an access token and return the access token.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: fail to get refresh token.
        """
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        token = self._client.get_cached_access_token(scopes)

        if not token:
            token = self._redeem_refresh_token(scopes, **kwargs)
        elif self._client.should_refresh(token):
            try:
                self._redeem_refresh_token(scopes, **kwargs)
            except Exception:  # pylint: disable=broad-except
                pass
        return token

    def _redeem_refresh_token(self, scopes, **kwargs):
        # type: (Sequence[str], **Any) -> Optional[AccessToken]
        if not self._refresh_token:
            self._refresh_token = get_credentials()
            if not self._refresh_token:
                raise CredentialUnavailableError(message="No Azure user is logged in to Visual Studio Code.")

        token = self._client.obtain_token_by_refresh_token(scopes, self._refresh_token, **kwargs)
        return token

    def get_token_refresh_options(self):
        # type: () -> dict
        return {"token_refresh_offset": self._client.token_refresh_offset}
