# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from typing import List, Optional, Any, cast, Dict

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.credentials_async import AsyncTokenCredential, AsyncSupportsTokenInfo
from ..._constants import EnvironmentVariables
from ..._internal import get_default_authority, normalize_authority, within_dac
from ..._credentials.default import parse_azure_dac
from .azure_cli import AzureCliCredential
from .azd_cli import AzureDeveloperCliCredential
from .azure_powershell import AzurePowerShellCredential
from .chained import ChainedTokenCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .shared_cache import SharedTokenCacheCredential
from .vscode import VisualStudioCodeCredential
from .workload_identity import WorkloadIdentityCredential


_LOGGER = logging.getLogger(__name__)


class DefaultAzureCredential(ChainedTokenCredential):
    """A credential capable of handling most Azure SDK authentication scenarios. See
    https://aka.ms/azsdk/python/identity/credential-chains#usage-guidance-for-defaultazurecredential.

    The identity it uses depends on the environment. When an access token is needed, it requests one using these
    identities in turn, stopping when one provides a token:

    1. A service principal configured by environment variables. See :class:`~azure.identity.aio.EnvironmentCredential`
       for more details.
    2. WorkloadIdentityCredential if environment variable configuration is set by the Azure workload
       identity webhook.
    3. An Azure managed identity. See :class:`~azure.identity.aio.ManagedIdentityCredential` for more details.
    4. On Windows only: a user who has signed in with a Microsoft application, such as Visual Studio. If multiple
       identities are in the cache, then the value of  the environment variable ``AZURE_USERNAME`` is used to select
       which identity to use. See :class:`~azure.identity.aio.SharedTokenCacheCredential` for more details.
    5. The identity currently logged in to the Azure CLI.
    6. The identity currently logged in to Azure PowerShell.
    7. The identity currently logged in to the Azure Developer CLI.

    This default behavior is configurable with keyword arguments.

    :keyword str authority: Authority of a Microsoft Entra endpoint, for example 'login.microsoftonline.com',
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds. Managed identities ignore this because they reside in a single cloud.
    :keyword str default_credential_allow_list: A semicolon-separated list of credential names.
        The default is to try all available credentials. If this is set, only the credentials in the list are tried.
        e.g. "ENVIRONMENT;CLI;MANAGED_IDENTITY" will only try EnvironmentCredential, AzureCliCredential, and
        ManagedIdentityCredential. All valid credential names are "DEVELOPER_CLI", "WORKLOAD_IDENTITY", "CLI",
        "ENVIRONMENT", "MANAGED_IDENTITY", "POWERSHELL" and "SHARED_CACHE".
    :keyword str managed_identity_client_id: The client ID of a user-assigned managed identity. Defaults to the value
        of the environment variable AZURE_CLIENT_ID, if any. If not specified, a system-assigned identity will be used.
    :keyword str workload_identity_client_id: The client ID of an identity assigned to the pod. Defaults to the value
        of the environment variable AZURE_CLIENT_ID, if any. If not specified, the pod's default identity will be used.
    :keyword str workload_identity_tenant_id: Preferred tenant for :class:`~azure.identity.WorkloadIdentityCredential`.
        Defaults to the value of environment variable AZURE_TENANT_ID, if any.
    :keyword str shared_cache_username: Preferred username for :class:`~azure.identity.aio.SharedTokenCacheCredential`.
        Defaults to the value of environment variable AZURE_USERNAME, if any.
    :keyword str shared_cache_tenant_id: Preferred tenant for :class:`~azure.identity.aio.SharedTokenCacheCredential`.
        Defaults to the value of environment variable AZURE_TENANT_ID, if any.
    :keyword str visual_studio_code_tenant_id: Tenant ID to use when authenticating with
        :class:`~azure.identity.aio.VisualStudioCodeCredential`. Defaults to the "Azure: Tenant" setting in VS Code's
        user settings or, when that setting has no value, the "organizations" tenant, which supports only Azure Active
        Directory work or school accounts.
    :keyword int process_timeout: The timeout in seconds to use for developer credentials that run
        subprocesses (e.g. AzureCliCredential, AzurePowerShellCredential). Defaults to **10** seconds.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_default_credential_async]
            :end-before: [END create_default_credential_async]
            :language: python
            :dedent: 4
            :caption: Create a DefaultAzureCredential.
    """

    def __init__(self, **kwargs: Any) -> None:
        # pylint: disable=too-many-statements, too-many-locals
        if "tenant_id" in kwargs:
            raise TypeError("'tenant_id' is not supported in DefaultAzureCredential.")

        authority: Optional[str] = kwargs.pop("authority", None)

        vscode_tenant_id = kwargs.pop(
            "visual_studio_code_tenant_id", os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        )
        vscode_args = dict(kwargs)
        if authority:
            vscode_args["authority"] = authority
        if vscode_tenant_id:
            vscode_args["tenant_id"] = vscode_tenant_id

        authority = normalize_authority(authority) if authority else get_default_authority()

        shared_cache_username = kwargs.pop("shared_cache_username", os.environ.get(EnvironmentVariables.AZURE_USERNAME))
        shared_cache_tenant_id = kwargs.pop(
            "shared_cache_tenant_id", os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        )

        managed_identity_client_id = kwargs.pop(
            "managed_identity_client_id", os.environ.get(EnvironmentVariables.AZURE_CLIENT_ID)
        )
        workload_identity_client_id = kwargs.pop("workload_identity_client_id", managed_identity_client_id)
        workload_identity_tenant_id = kwargs.pop(
            "workload_identity_tenant_id", os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        )

        vscode_tenant_id = kwargs.pop(
            "visual_studio_code_tenant_id", os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        )

        process_timeout = kwargs.pop("process_timeout", 10)

        exclude_workload_identity_credential = kwargs.pop("exclude_workload_identity_credential", False)
        exclude_visual_studio_code_credential = kwargs.pop("exclude_visual_studio_code_credential", True)
        exclude_developer_cli_credential = kwargs.pop("exclude_developer_cli_credential", False)
        exclude_cli_credential = kwargs.pop("exclude_cli_credential", False)
        exclude_environment_credential = kwargs.pop("exclude_environment_credential", False)
        exclude_managed_identity_credential = kwargs.pop("exclude_managed_identity_credential", False)
        exclude_shared_token_cache_credential = kwargs.pop("exclude_shared_token_cache_credential", False)
        exclude_powershell_credential = kwargs.pop("exclude_powershell_credential", False)

        credentials: List[AsyncSupportsTokenInfo] = []
        avail_credentials: Dict[str, Any] = {}
        within_dac.set(True)
        if not exclude_environment_credential:
            env_cred = EnvironmentCredential(authority=authority, _within_dac=True, **kwargs)
            avail_credentials["ENVIRONMENT"] = env_cred
            credentials.append(env_cred)
        if not exclude_workload_identity_credential:
            if all(os.environ.get(var) for var in EnvironmentVariables.WORKLOAD_IDENTITY_VARS):
                client_id = workload_identity_client_id
                workload_cred = WorkloadIdentityCredential(
                    client_id=cast(str, client_id),
                    tenant_id=workload_identity_tenant_id,
                    token_file_path=os.environ[EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE],
                    **kwargs
                )
                avail_credentials["WORKLOAD_IDENTITY"] = workload_cred
                credentials.append(workload_cred)
        if not exclude_managed_identity_credential:
            mi_cred = ManagedIdentityCredential(
                client_id=managed_identity_client_id,
                _exclude_workload_identity_credential=exclude_workload_identity_credential,
                **kwargs
            )
            avail_credentials["MANAGED_IDENTITY"] = mi_cred
            credentials.append(mi_cred)
        if not exclude_shared_token_cache_credential and SharedTokenCacheCredential.supported():
            try:
                # username and/or tenant_id are only required when the cache contains tokens for multiple identities
                shared_cache = SharedTokenCacheCredential(
                    username=shared_cache_username, tenant_id=shared_cache_tenant_id, authority=authority, **kwargs
                )
                avail_credentials["SHARED_CACHE"] = shared_cache
                credentials.append(shared_cache)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.info("Shared token cache is unavailable: '%s'", ex)
        if not exclude_visual_studio_code_credential:
            vscode_cred = VisualStudioCodeCredential(**vscode_args)
            avail_credentials["VISUAL_STUDIO_CODE"] = vscode_cred
            credentials.append(vscode_cred)
        if not exclude_cli_credential:
            cli_cred = AzureCliCredential(process_timeout=process_timeout)
            avail_credentials["CLI"] = cli_cred
            credentials.append(cli_cred)
        if not exclude_powershell_credential:
            ps_cred = AzurePowerShellCredential(process_timeout=process_timeout)
            avail_credentials["POWERSHELL"] = ps_cred
            credentials.append(ps_cred)
        if not exclude_developer_cli_credential:
            dev_cli_cred = AzureDeveloperCliCredential(process_timeout=process_timeout)
            avail_credentials["DEVELOPER_CLI"] = dev_cli_cred
            credentials.append(dev_cli_cred)
        default_credential_allow_list = kwargs.pop(
            "default_credential_allow_list", os.environ.get("AZURE_DEFAULT_CREDENTIAL_ALLOW_LIST")
        )
        if default_credential_allow_list:
            default_credential_allow_list = default_credential_allow_list.upper()
            credentials = parse_azure_dac(default_credential_allow_list, avail_credentials)
        within_dac.set(False)
        super().__init__(*credentials)

    async def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        """Asynchronously request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The exception has a
          `message` attribute listing each authentication attempt and its error message.
        """
        if self._successful_credential:
            token = await cast(AsyncTokenCredential, self._successful_credential).get_token(
                *scopes, claims=claims, tenant_id=tenant_id, **kwargs
            )
            _LOGGER.info(
                "%s acquired a token from %s", self.__class__.__name__, self._successful_credential.__class__.__name__
            )
            return token

        within_dac.set(True)
        token = await super().get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)
        within_dac.set(False)
        return token

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Asynchronously request an access token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.

        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The exception has a
           `message` attribute listing each authentication attempt and its error message.
        """
        if self._successful_credential:
            token_info = await cast(AsyncSupportsTokenInfo, self._successful_credential).get_token_info(
                *scopes, options=options
            )
            _LOGGER.info(
                "%s acquired a token from %s", self.__class__.__name__, self._successful_credential.__class__.__name__
            )
            return token_info

        within_dac.set(True)
        token_info = await cast(AsyncSupportsTokenInfo, super()).get_token_info(*scopes, options=options)
        within_dac.set(False)
        return token_info
