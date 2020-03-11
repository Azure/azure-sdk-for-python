# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""A thin wrapper around MSAL's token cache and OAuth 2 client"""

import time
from typing import TYPE_CHECKING

from azure.core.credentials import AccessToken

from .aad_client_base import AadClientBase
from .msal_transport_adapter import MsalTransportAdapter
from .exception_wrapper import wrap_exceptions

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Iterable


class AadClient(AadClientBase):
    def _get_client_session(self, **kwargs):
        return MsalTransportAdapter(**kwargs)

    @wrap_exceptions
    def _obtain_token(self, scopes, fn, **kwargs):  # pylint:disable=unused-argument
        # type: (Iterable[str], Callable, **Any) -> AccessToken
        now = int(time.time())
        response = fn()
        return self._process_response(response=response, scopes=scopes, now=now)
