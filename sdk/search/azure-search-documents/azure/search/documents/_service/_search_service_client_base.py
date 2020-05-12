# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from .._headers_mixin import HeadersMixin
from ._datasources_client import SearchDataSourcesClient
from ._indexes_client import SearchIndexesClient
from ._indexers_client import SearchIndexersClient
from ._skillsets_client import SearchSkillsetsClient
from ._synonym_maps_client import SearchSynonymMapsClient

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

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_search_service_with_key]
            :end-before: [END create_search_service_with_key]
            :language: python
            :dedent: 4
            :caption: Creating the SearchServiceClient with an API key.
    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(self, endpoint, credential):
        # type: (str, AzureKeyCredential) -> None

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
            elif not endpoint.lower().startswith('https'):
                raise ValueError("Bearer token authentication is not permitted for non-TLS protected (non-https) URLs.")
        except AttributeError:
            raise ValueError("Endpoint must be a string.")

        self._endpoint = endpoint  # type: str
        self._credential = credential  # type: AzureKeyCredential

    def __repr__(self):
        # type: () -> str
        return "<SearchServiceClient [endpoint={}]>".format(repr(self._endpoint))[:1024]
