# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Any, List, Union, Dict, Optional

import msal

from .msal_client import MsalClient
from .utils import get_default_authority, normalize_authority, resolve_tenant, validate_tenant_id
from .._constants import EnvironmentVariables
from .._persistent_cache import _load_persistent_cache


class MsalCredential:   # pylint: disable=too-many-instance-attributes
    """Base class for credentials wrapping MSAL applications"""

    def __init__(
            self,
            client_id: str,
            client_credential: Optional[Union[str, Dict]] = None,
            *,
            additionally_allowed_tenants: Optional[List[str]] = None,
            # allow_broker: Optional[bool] = None,
            authority: Optional[str] = None,
            disable_instance_discovery: Optional[bool] = None,
            tenant_id: Optional[str] = None,
            **kwargs
    ) -> None:
        self._instance_discovery = None if disable_instance_discovery is None\
            else not disable_instance_discovery
        self._authority = normalize_authority(authority) if authority else get_default_authority()
        self._regional_authority = os.environ.get(EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME)
        if self._regional_authority and self._regional_authority.lower() in ["tryautodetect", "true"]:
            self._regional_authority = msal.ConfidentialClientApplication.ATTEMPT_REGION_DISCOVERY
        self._tenant_id = tenant_id or "organizations"
        validate_tenant_id(self._tenant_id)
        self._client = MsalClient(**kwargs)
        self._client_applications: Dict[str, msal.ClientApplication] = {}
        self._client_credential = client_credential
        self._client_id = client_id
        # self._allow_broker = allow_broker
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

    def close(self) -> None:
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
            capabilities = None if EnvironmentVariables.AZURE_IDENTITY_DISABLE_CP1 in os.environ else ["CP1"]
            cls = msal.ConfidentialClientApplication if self._client_credential else msal.PublicClientApplication
            self._client_applications[tenant_id] = cls(
                client_id=self._client_id,
                client_credential=self._client_credential,
                client_capabilities=capabilities,
                authority="{}/{}".format(self._authority, tenant_id),
                azure_region=self._regional_authority,
                token_cache=self._cache,
                http_client=self._client,
                instance_discovery=self._instance_discovery,
                # allow_broker=self._allow_broker
            )

        return self._client_applications[tenant_id]
