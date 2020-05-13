# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from .._headers_mixin import HeadersMixin
from ._utils import _normalize_endpoint

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Dict, List, Optional, Sequence
    from azure.core.credentials import AzureKeyCredential


class SearchServiceClientBase(HeadersMixin):  # pylint: disable=too-many-public-methods
    """A client to interact with an existing Azure search service.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials import AzureKeyCredential
    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(self, endpoint, credential):
        # type: (str, AzureKeyCredential) -> None

        self._endpoint = _normalize_endpoint(endpoint)  # type: str
        self._credential = credential  # type: AzureKeyCredential

    def __repr__(self):
        # type: () -> str
        return "<SearchServiceClient [endpoint={}]>".format(repr(self._endpoint))[:1024]
