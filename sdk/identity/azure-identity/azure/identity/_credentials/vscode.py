# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Any, Optional

import msal
from azure.core.credentials import AccessToken, TokenRequestOptions, AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError

from .._auth_record import AuthenticationRecord
from .._exceptions import CredentialUnavailableError
from .._constants import AZURE_VSCODE_CLIENT_ID
from .._internal import within_dac

from .._internal.decorators import log_get_token
from .._internal.utils import get_broker_credential


VSCODE_AUTH_RECORD_PATH = "~/.azure/ms-azuretools.vscode-azureresourcegroups/authRecord.json"


def load_vscode_auth_record() -> Optional[AuthenticationRecord]:
    """Load the authentication record corresponding to a known location.

    This will load from ~/.azure/ms-azuretools.vscode-azureresourcegroups/authRecord.json

    :return: The authentication record if it exists, otherwise None.
    :rtype: Optional[AuthenticationRecord]
    :raises: ValueError if the authentication record is not in the expected format
    """

    auth_record_path = os.path.expanduser(VSCODE_AUTH_RECORD_PATH)
    if not os.path.exists(auth_record_path):
        return None

    with open(auth_record_path, "r", encoding="utf-8") as f:
        json_string = f.read()

    # TODO: Validate the JSON structure and schema.
    return AuthenticationRecord.deserialize(json_string)


class VisualStudioCodeCredential:
    """Authenticates as the Azure user signed in to Visual Studio Code via the 'Azure Resources' extension.

    :keyword str authority: Authority of a Microsoft Entra endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword str tenant_id: a Microsoft Entra tenant ID. Defaults to the "organizations" tenant, which can
        authenticate work or school accounts.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(self, **kwargs: Any) -> None:

        broker_credential_class = get_broker_credential()
        if broker_credential_class:
            authentication_record = load_vscode_auth_record()
            self._broker_credential = broker_credential_class(
                client_id=AZURE_VSCODE_CLIENT_ID,
                authentication_record=authentication_record,
                parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE,
                use_default_broker_acount=True,
                **kwargs
            )
        self._unavailable_message = (
            "VisualStudioCodeCredential requires the 'azure-identity-broker' package to be installed. "
            "You must also ensure you have the Azure Resources extension installed and have "
            "signed in to Azure via Visual Studio Code."
        )

    def __enter__(self) -> "VisualStudioCodeCredential":
        if self._broker_credential:
            self._broker_credential.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._broker_credential:
            self._broker_credential.__exit__(*args)

    def close(self) -> None:
        """Close the credential's transport session."""
        if self._broker_credential:
            self._broker_credential.close()

    @log_get_token
    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        """Request an access token for `scopes` as the user currently signed in to Visual Studio Code.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises ~azure.identity.CredentialUnavailableError: the credential cannot retrieve user details from Visual
          Studio Code
        """
        if not self._broker_credential:
            raise CredentialUnavailableError(message=self._unavailable_message)
        if within_dac.get():
            try:
                token = self._broker_credential.get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)
                return token
            except ClientAuthenticationError as ex:
                raise CredentialUnavailableError(message=ex.message) from ex
        return self._broker_credential.get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes` as the user currently signed in to Visual Studio Code.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.
        :raises ~azure.identity.CredentialUnavailableError: the credential cannot retrieve user details from Visual
          Studio Code.
        """
        if not self._broker_credential:
            raise CredentialUnavailableError(message=self._unavailable_message)
        if within_dac.get():
            try:
                token = self._broker_credential.get_token_info(*scopes, options=options)
                return token
            except ClientAuthenticationError as ex:
                raise CredentialUnavailableError(message=ex.message) from ex
        return self._broker_credential.get_token_info(*scopes, options=options)
