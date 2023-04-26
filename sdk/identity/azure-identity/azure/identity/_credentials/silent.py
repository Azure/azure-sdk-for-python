# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import platform
import time
from typing import Dict, Optional, Any

from msal import PublicClientApplication

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .. import CredentialUnavailableError
from .._internal import resolve_tenant, validate_tenant_id
from .._internal.decorators import wrap_exceptions
from .._internal.msal_client import MsalClient
from .._internal.shared_token_cache import NO_TOKEN
from .._persistent_cache import _load_persistent_cache, TokenCachePersistenceOptions
from .._constants import EnvironmentVariables
from .. import AuthenticationRecord


class SilentAuthenticationCredential:
    """Internal class for authenticating from the default shared cache given an AuthenticationRecord"""

    def __init__(
            self,
            authentication_record: AuthenticationRecord,
            *,
            tenant_id: Optional[str] = None,
            **kwargs
    ) -> None:
        self._auth_record = authentication_record

        # authenticate in the tenant that produced the record unless "tenant_id" specifies another
        self._tenant_id = tenant_id or self._auth_record.tenant_id
        validate_tenant_id(self._tenant_id)
        self._cache = kwargs.pop("_cache", None)
        self._cache_persistence_options = kwargs.pop("cache_persistence_options", None)
        self._client_applications: Dict[str, PublicClientApplication] = {}
        self._additionally_allowed_tenants = kwargs.pop("additionally_allowed_tenants", [])
        self._client = MsalClient(**kwargs)
        self._initialized = False

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        if not scopes:
            raise ValueError('"get_token" requires at least one scope')

        if not self._initialized:
            self._initialize()

        if not self._cache:
            raise CredentialUnavailableError(message="Shared token cache unavailable")

        return self._acquire_token_silent(*scopes, **kwargs)

    def _initialize(self):
        if not self._cache and platform.system() in {"Darwin", "Linux", "Windows"}:
            try:
                # If no cache options were provided, the default cache will be used. This credential accepts the
                # user's default cache regardless of whether it's encrypted. It doesn't create a new cache. If the
                # default cache exists, the user must have created it earlier. If it's unencrypted, the user must
                # have allowed that.
                options = self._cache_persistence_options or \
                    TokenCachePersistenceOptions(allow_unencrypted_storage=True)
                self._cache = _load_persistent_cache(options)
            except Exception:  # pylint:disable=broad-except
                pass

        self._initialized = True

    def _get_client_application(self, **kwargs: Any):
        tenant_id = resolve_tenant(
            self._tenant_id,
            additionally_allowed_tenants=self._additionally_allowed_tenants,
            **kwargs
        )
        if tenant_id not in self._client_applications:
            # CP1 = can handle claims challenges (CAE)
            capabilities = None if EnvironmentVariables.AZURE_IDENTITY_DISABLE_CP1 in os.environ else ["CP1"]
            self._client_applications[tenant_id] = PublicClientApplication(
                client_id=self._auth_record.client_id,
                authority="https://{}/{}".format(self._auth_record.authority, tenant_id),
                token_cache=self._cache,
                http_client=self._client,
                client_capabilities=capabilities
            )
        return self._client_applications[tenant_id]

    @wrap_exceptions
    def _acquire_token_silent(self, *scopes: str, **kwargs: Any) -> AccessToken:
        """Silently acquire a token from MSAL."""

        result = None

        client_application = self._get_client_application(**kwargs)
        accounts_for_user = client_application.get_accounts(username=self._auth_record.username)
        if not accounts_for_user:
            raise CredentialUnavailableError("The cache contains no account matching the given AuthenticationRecord.")

        for account in accounts_for_user:
            if account.get("home_account_id") != self._auth_record.home_account_id:
                continue

            now = int(time.time())
            result = client_application.acquire_token_silent_with_error(
                list(scopes), account=account, claims_challenge=kwargs.get("claims")
            )
            if result and "access_token" in result and "expires_in" in result:
                return AccessToken(result["access_token"], now + int(result["expires_in"]))

        # if we get this far, the cache contained a matching account but MSAL failed to authenticate it silently
        if result:
            # cache contains a matching refresh token but STS returned an error response when MSAL tried to use it
            message = "Token acquisition failed"
            details = result.get("error_description") or result.get("error")
            if details:
                message += ": {}".format(details)
            raise ClientAuthenticationError(message=message)

        # cache doesn't contain a matching refresh (or access) token
        raise CredentialUnavailableError(message=NO_TOKEN.format(self._auth_record.username))
