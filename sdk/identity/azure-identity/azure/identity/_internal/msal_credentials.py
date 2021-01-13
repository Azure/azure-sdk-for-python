# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc

import msal

from .msal_client import MsalClient
from .._internal import _TokenCache, get_default_authority, normalize_authority, validate_tenant_id

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports,unused-import
    from typing import Any, Mapping, Optional, Type, Union


class MsalCredential(ABC):
    """Base class for credentials wrapping MSAL applications"""

    def __init__(self, client_id, client_credential=None, **kwargs):
        # type: (str, Optional[Union[str, dict]], **Any) -> None
        authority = kwargs.pop("authority", None)
        self._authority = normalize_authority(authority) if authority else get_default_authority()
        self._tenant_id = kwargs.pop("tenant_id", None) or "organizations"
        validate_tenant_id(self._tenant_id)

        self._client_credential = client_credential
        self._client_id = client_id

        self._cache = kwargs.pop("token_cache", None) or _TokenCache()
        self._client = MsalClient(**kwargs)

        # postpone creating the wrapped application because its initializer uses the network
        self._msal_app = None  # type: Optional[msal.ClientApplication]
        super(MsalCredential, self).__init__()

    @abc.abstractmethod
    def _get_app(self):
        # type: () -> msal.ClientApplication
        pass

    def _create_app(self, cls, **kwargs):
        # type: (Type[msal.ClientApplication], **Any) -> msal.ClientApplication
        app = cls(
            client_id=self._client_id,
            client_credential=self._client_credential,
            authority="{}/{}".format(self._authority, self._tenant_id),
            token_cache=self._cache._cache,  # pylint:disable=protected-access
            http_client=self._client,
            **kwargs
        )

        return app
