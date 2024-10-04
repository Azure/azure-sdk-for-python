# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from typing import Optional, Any, Mapping, cast

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions, TokenCredential, SupportsTokenInfo
from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal.decorators import log_get_token


_LOGGER = logging.getLogger(__name__)


def validate_identity_config(client_id: Optional[str], identity_config: Optional[Mapping[str, str]]) -> None:
    if identity_config:
        if client_id:
            if any(key in identity_config for key in ("object_id", "resource_id", "client_id")):
                raise ValueError(
                    "identity_config must not contain 'object_id', 'resource_id', or 'client_id' when 'client_id' is "
                    "provided as a keyword argument."
                )
        # Only one of these keys should be present if one is present.
        valid_keys = {"object_id", "resource_id", "client_id"}
        if len(identity_config.keys() & valid_keys) > 1:
            raise ValueError(
                f"identity_config must not contain more than one of the following keys: {', '.join(valid_keys)}"
            )


class ManagedIdentityCredential:
    """Authenticates with an Azure managed identity in any hosting environment which supports managed identities.

    This credential defaults to using a system-assigned identity. To configure a user-assigned identity, use one of
    the keyword arguments. See `Microsoft Entra ID documentation
    <https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview>`__ for more
    information about configuring managed identity for applications.

    :keyword str client_id: a user-assigned identity's client ID or, when using Pod Identity, the client ID of a
       Microsoft Entra app registration. This argument is supported in all hosting environments.
    :keyword identity_config: a mapping ``{parameter_name: value}`` specifying a user-assigned identity by its object
        or resource ID, for example ``{"object_id": "..."}``. Check the documentation for your hosting environment to
        learn what values it expects.
    :paramtype identity_config: Mapping[str, str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_managed_identity_credential]
            :end-before: [END create_managed_identity_credential]
            :language: python
            :dedent: 4
            :caption: Create a ManagedIdentityCredential.
    """

    def __init__(
        self, *, client_id: Optional[str] = None, identity_config: Optional[Mapping[str, str]] = None, **kwargs: Any
    ) -> None:
        validate_identity_config(client_id, identity_config)
        self._credential: Optional[SupportsTokenInfo] = None
        exclude_workload_identity = kwargs.pop("_exclude_workload_identity_credential", False)
        if os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT):
            if os.environ.get(EnvironmentVariables.IDENTITY_HEADER):
                if os.environ.get(EnvironmentVariables.IDENTITY_SERVER_THUMBPRINT):
                    _LOGGER.info("%s will use Service Fabric managed identity", self.__class__.__name__)
                    from .service_fabric import ServiceFabricCredential

                    self._credential = ServiceFabricCredential(
                        client_id=client_id, identity_config=identity_config, **kwargs
                    )
                else:
                    _LOGGER.info("%s will use App Service managed identity", self.__class__.__name__)
                    from .app_service import AppServiceCredential

                    self._credential = AppServiceCredential(
                        client_id=client_id, identity_config=identity_config, **kwargs
                    )
            elif os.environ.get(EnvironmentVariables.IMDS_ENDPOINT):
                _LOGGER.info("%s will use Azure Arc managed identity", self.__class__.__name__)
                from .azure_arc import AzureArcCredential

                self._credential = AzureArcCredential(client_id=client_id, identity_config=identity_config, **kwargs)
        elif os.environ.get(EnvironmentVariables.MSI_ENDPOINT):
            if os.environ.get(EnvironmentVariables.MSI_SECRET):
                _LOGGER.info("%s will use Azure ML managed identity", self.__class__.__name__)
                from .azure_ml import AzureMLCredential

                self._credential = AzureMLCredential(client_id=client_id, identity_config=identity_config, **kwargs)
            else:
                _LOGGER.info("%s will use Cloud Shell managed identity", self.__class__.__name__)
                from .cloud_shell import CloudShellCredential

                self._credential = CloudShellCredential(client_id=client_id, identity_config=identity_config, **kwargs)
        elif (
            all(os.environ.get(var) for var in EnvironmentVariables.WORKLOAD_IDENTITY_VARS)
            and not exclude_workload_identity
        ):
            _LOGGER.info("%s will use workload identity", self.__class__.__name__)
            from .workload_identity import WorkloadIdentityCredential

            workload_client_id = client_id or os.environ.get(EnvironmentVariables.AZURE_CLIENT_ID)
            if not workload_client_id:
                raise ValueError('Configure the environment with a client ID or pass a value for "client_id" argument')

            self._credential = WorkloadIdentityCredential(
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                client_id=workload_client_id,
                file=os.environ[EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE],
                **kwargs,
            )
        else:
            from .imds import ImdsCredential

            _LOGGER.info("%s will use IMDS", self.__class__.__name__)
            self._credential = ImdsCredential(client_id=client_id, identity_config=identity_config, **kwargs)

    def __enter__(self) -> "ManagedIdentityCredential":
        if self._credential:
            self._credential.__enter__()  # type: ignore
        return self

    def __exit__(self, *args: Any) -> None:
        if self._credential:
            self._credential.__exit__(*args)  # type: ignore

    def close(self) -> None:
        """Close the credential's transport session."""
        self.__exit__()

    @log_get_token
    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.

        :keyword str claims: not used by this credential; any value provided will be ignored.
        :keyword str tenant_id: not used by this credential; any value provided will be ignored.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises ~azure.identity.CredentialUnavailableError: managed identity isn't available in the hosting environment
        """

        if not self._credential:
            raise CredentialUnavailableError(
                message="No managed identity endpoint found. \n"
                "The Target Azure platform could not be determined from environment variables. \n"
                "Visit https://aka.ms/azsdk/python/identity/managedidentitycredential/troubleshoot to "
                "troubleshoot this issue."
            )
        return cast(TokenCredential, self._credential).get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

    @log_get_token
    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.
        :raises ~azure.identity.CredentialUnavailableError: managed identity isn't available in the hosting environment.
        """
        if not self._credential:
            raise CredentialUnavailableError(
                message="No managed identity endpoint found. \n"
                "The Target Azure platform could not be determined from environment variables. \n"
                "Visit https://aka.ms/azsdk/python/identity/managedidentitycredential/troubleshoot to "
                "troubleshoot this issue."
            )
        return cast(SupportsTokenInfo, self._credential).get_token_info(*scopes, options=options)
