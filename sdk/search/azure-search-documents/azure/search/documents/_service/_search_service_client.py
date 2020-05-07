# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.tracing.decorator import distributed_trace

from ._generated import SearchServiceClient as _SearchServiceClient
from .._headers_mixin import HeadersMixin
from .._version import SDK_MONIKER
from ._datasources_client import SearchDataSourcesClient
from ._indexes_client import SearchIndexesClient
from ._indexers_client import SearchIndexersClient
from ._skillsets_client import SearchSkillsetsClient
from ._synonym_maps_client import SearchSynonymMapsClient

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Dict, List, Optional, Sequence
    from azure.core.credentials import AzureKeyCredential


class SearchServiceClient(HeadersMixin):  # pylint: disable=too-many-public-methods
    """A client to interact with an existing Azure search service.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_search_service_client_with_key]
            :end-before: [END create_search_service_client_with_key]
            :language: python
            :dedent: 4
            :caption: Creating the SearchServiceClient with an API key.
    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, **Any) -> None

        self._endpoint = endpoint  # type: str
        self._credential = credential  # type: AzureKeyCredential
        self._client = _SearchServiceClient(
            endpoint=endpoint, sdk_moniker=SDK_MONIKER, **kwargs
        )  # type: _SearchServiceClient

        self._indexes_client = SearchIndexesClient(endpoint, credential, **kwargs)

        self._synonym_maps_client = SearchSynonymMapsClient(
            endpoint, credential, **kwargs
        )

        self._skillsets_client = SearchSkillsetsClient(endpoint, credential, **kwargs)

        self._datasources_client = SearchDataSourcesClient(
            endpoint, credential, **kwargs
        )

        self._indexers_client = SearchIndexersClient(endpoint, credential, **kwargs)

    def __repr__(self):
        # type: () -> str
        return "<SearchServiceClient [endpoint={}]>".format(repr(self._endpoint))[:1024]

    def __enter__(self):
        # type: () -> SearchServiceClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        return self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.SearchServiceClient` session.

        """
        return self._client.close()

    @distributed_trace
    def get_service_statistics(self, **kwargs):
        # type: (**Any) -> dict
        """Get service level statistics for a search service.

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.get_service_statistics(**kwargs)
        return result.as_dict()

    def get_indexes_client(self):
        # type: () -> SearchIndexesClient
        """Return a client to perform operations on Search Indexes.

        :return: The Search Indexes client
        :rtype: SearchIndexesClient
        """
        return self._indexes_client

    def get_synonym_maps_client(self):
        # type: () -> SearchSynonymMapsClient
        """Return a client to perform operations on Synonym Maps.

        :return: The Synonym Maps client
        :rtype: SearchSynonymMapsClient
        """
        return self._synonym_maps_client

    def get_skillsets_client(self):
        # type: () -> SearchSkillsetsClient
        """Return a client to perform operations on Skillsets.

        :return: The Skillsets client
        :rtype: SearchSkillsetClient
        """
        return self._skillsets_client

    def get_datasources_client(self):
        # type: () -> SearchDataSourcesClient
        """Return a client to perform operations on Data Sources.

        :return: The Data Sources client
        :rtype: SearchDataSourcesClient
        """
        return self._datasources_client

    def get_indexers_client(self):
        # type: () -> SearchIndexersClient
        """Return a client to perform operations on Data Sources.

        :return: The Data Sources client
        :rtype: SearchDataSourcesClient
        """
        return self._indexers_client
