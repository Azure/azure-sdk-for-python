# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Any, List, Union, Dict

import msal

from .msal_client import MsalClient
from .utils import get_default_authority, normalize_authority, resolve_tenant, validate_tenant_id
from .._constants import EnvironmentVariables
from .._persistent_cache import _load_persistent_cache


class MsalCredential(object):
    """Base class for credentials wrapping MSAL applications"""

    def __init__(
            self,
            client_id: str,
            client_credential: Union[str, Dict] = None,
            *,
            additionally_allowed_tenants: List[str] = None,
            **kwargs
    ) -> None:
        authority = kwargs.pop("authority", None)
        # self._validate_authority = kwargs.pop("validate_authority", True)
        self._authority = normalize_authority(authority) if authority else get_default_authority()
        self._regional_authority = os.environ.get(EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME)
        self._tenant_id = kwargs.pop("tenant_id", None) or "organizations"
        validate_tenant_id(self._tenant_id)
        self._client = MsalClient(**kwargs)
        self._client_applications = {}  # type: Dict[str, msal.ClientApplication]
        self._client_credential = client_credential
        self._client_id = client_id
        self._additionally_allowed_tenants = additionally_allowed_tenants or []

        self._cache = kwargs.pop("_cache", None)
        if not self._cache:
            options = kwargs.pop("cache_persistence_options", None)
            if options:
                self._cache = _load_persistent_cache(options)
            else:
                self._cache = msal.TokenCache()

        super(MsalCredential, self).__init__()

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self):
        # type: () -> None
        self.__exit__()

    def _get_app(self, **kwargs):
        # type: (**Any) -> msal.ClientApplication
        tenant_id = resolve_tenant(
            self._tenant_id,
            additionally_allowed_tenants=self._additionally_allowed_tenants,
            **kwargs
        )
        if tenant_id not in self._client_applications:
            # CP1 = can handle claims challenges (CAE)
            capabilities = None if "AZURE_IDENTITY_DISABLE_CP1" in os.environ else ["CP1"]
            cls = msal.ConfidentialClientApplication if self._client_credential else msal.PublicClientApplication
            self._client_applications[tenant_id] = cls(
                client_id=self._client_id,
                client_credential=self._client_credential,
                client_capabilities=capabilities,
                authority="{}/{}".format(self._authority, tenant_id),
                azure_region=self._regional_authority,
                token_cache=self._cache,
                http_client=self._client,
                # validate_authority=self._validate_authority
            )

        return self._client_applications[tenant_id]
