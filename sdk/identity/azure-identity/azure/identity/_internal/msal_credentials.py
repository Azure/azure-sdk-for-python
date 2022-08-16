# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import msal

from .msal_client import MsalClient
from .._constants import EnvironmentVariables
from .._internal import get_default_authority, normalize_authority, resolve_tenant, validate_tenant_id
from .._persistent_cache import _load_persistent_cache

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports,unused-import
    from typing import Any, Dict, Optional, Union


class MsalCredential(object):
    """Base class for credentials wrapping MSAL applications"""

    def __init__(self, client_id, client_credential=None, **kwargs):
        # type: (str, Optional[Union[str, Dict]], **Any) -> None
        authority = kwargs.pop("authority", None)
        self._known_authority_hosts = kwargs.pop("known_authority_hosts", None)
        self._authority = normalize_authority(authority) if authority else get_default_authority()
        self._regional_authority = os.environ.get(EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME)
        self._tenant_id = kwargs.pop("tenant_id", None) or "organizations"
        validate_tenant_id(self._tenant_id)
        self._client = MsalClient(**kwargs)
        self._client_applications = {}  # type: Dict[str, msal.ClientApplication]
        self._client_credential = client_credential
        self._client_id = client_id

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
        tenant_id = resolve_tenant(self._tenant_id, **kwargs)
        if tenant_id not in self._client_applications:
            # CP1 = can handle claims challenges (CAE)
            capabilities = None if "AZURE_IDENTITY_DISABLE_CP1" in os.environ else ["CP1"]
            cls = msal.ConfidentialClientApplication if self._client_credential else msal.PublicClientApplication
            if self._known_authority_hosts:
                cls.set_known_authority_hosts(self._known_authority_hosts)
            self._client_applications[tenant_id] = cls(
                client_id=self._client_id,
                client_credential=self._client_credential,
                client_capabilities=capabilities,
                authority="{}/{}".format(self._authority, tenant_id),
                azure_region=self._regional_authority,
                token_cache=self._cache,
                http_client=self._client,
            )

        return self._client_applications[tenant_id]
