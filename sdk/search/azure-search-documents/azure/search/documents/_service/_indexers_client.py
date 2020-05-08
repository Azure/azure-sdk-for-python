# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core import MatchConditions
from azure.core.tracing.decorator import distributed_trace

from ._generated import SearchServiceClient as _SearchServiceClient
from ._utils import get_access_conditions
from .._headers_mixin import HeadersMixin
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from ._generated.models import SearchIndexer, SearchIndexerStatus
    from typing import Any, Dict, Optional, Sequence
    from azure.core.credentials import AzureKeyCredential


class SearchIndexersClient(HeadersMixin):
    """A client to interact with Azure search service Indexers.

    This class is not normally instantiated directly, instead use
    `get_indexers_client()` from a `SearchServiceClient`

    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, **Any) -> None

        self._endpoint = endpoint  # type: str
        self._credential = credential  # type: AzureKeyCredential
        self._client = _SearchServiceClient(
            endpoint=endpoint, sdk_moniker=SDK_MONIKER, **kwargs
        )  # type: _SearchServiceClient

    def __enter__(self):
        # type: () -> SearchIndexersClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        return self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.SearchIndexersClient` session.

        """
        return self._client.close()

    @distributed_trace
    def create_indexer(self, indexer, **kwargs):
        # type: (SearchIndexer, **Any) -> SearchIndexer
        """Creates a new SearchIndexer.

        :param indexer: The definition of the indexer to create.
        :type indexer: ~~azure.search.documents.SearchIndexer
        :return: The created SearchIndexer
        :rtype: ~azure.search.documents.SearchIndexer

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexer_operations.py
                :start-after: [START create_indexer]
                :end-before: [END create_indexer]
                :language: python
                :dedent: 4
                :caption: Create a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.indexers.create(indexer, **kwargs)
        return result

    @distributed_trace
    def create_or_update_indexer(self, indexer, name=None, **kwargs):
        # type: (SearchIndexer, Optional[str], **Any) -> SearchIndexer
        """Creates a new indexer or updates a indexer if it already exists.

        :param name: The name of the indexer to create or update.
        :type name: str
        :param indexer: The definition of the indexer to create or update.
        :type indexer: ~azure.search.documents.SearchIndexer
        :return: The created IndexSearchIndexerer
        :rtype: ~azure.search.documents.SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            indexer, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        if not name:
            name = indexer.name
        result = self._client.indexers.create_or_update(
            indexer_name=name, indexer=indexer, error_map=error_map, **kwargs
        )
        return result

    @distributed_trace
    def get_indexer(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndexer
        """Retrieves a indexer definition.

        :param name: The name of the indexer to retrieve.
        :type name: str
        :return: The SearchIndexer that is fetched.
        :rtype: ~azure.search.documents.SearchIndexer

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexer_operations.py
                :start-after: [START get_indexer]
                :end-before: [END get_indexer]
                :language: python
                :dedent: 4
                :caption: Retrieve a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.indexers.get(name, **kwargs)
        return result

    @distributed_trace
    def get_indexers(self, **kwargs):
        # type: (**Any) -> Sequence[SearchIndexer]
        """Lists all indexers available for a search service.

        :return: List of all the SearchIndexers.
        :rtype: `list[dict]`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexer_operations.py
                :start-after: [START list_indexer]
                :end-before: [END list_indexer]
                :language: python
                :dedent: 4
                :caption: List all the SearchIndexers
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.indexers.list(**kwargs)
        return result.indexers

    @distributed_trace
    def delete_indexer(self, indexer, **kwargs):
        # type: (Union[str, SearchIndexer], **Any) -> None
        """Deletes an indexer. To use access conditions, the SearchIndexer model
        must be provided instead of the name. It is enough to provide
        the name of the indexer to delete unconditionally.

        :param indexer: The indexer to delete.
        :type indexer: str or ~azure.search.documents.SearchIndexer
        :keyword match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions

        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexer_operations.py
                :start-after: [START delete_indexer]
                :end-before: [END delete_indexer]
                :language: python
                :dedent: 4
                :caption: Delete a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            indexer, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        try:
            name = indexer.name
        except AttributeError:
            name = indexer
        self._client.indexers.delete(name, error_map=error_map, **kwargs)

    @distributed_trace
    def run_indexer(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Run an indexer.

        :param name: The name of the indexer to run.
        :type name: str

        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexer_operations.py
                :start-after: [START run_indexer]
                :end-before: [END run_indexer]
                :language: python
                :dedent: 4
                :caption: Run a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        self._client.indexers.run(name, **kwargs)

    @distributed_trace
    def reset_indexer(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Resets the change tracking state associated with an indexer.

        :param name: The name of the indexer to reset.
        :type name: str

        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexer_operations.py
                :start-after: [START reset_indexer]
                :end-before: [END reset_indexer]
                :language: python
                :dedent: 4
                :caption: Reset a SearchIndexer's change tracking state
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        self._client.indexers.reset(name, **kwargs)

    @distributed_trace
    def get_indexer_status(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndexerStatus
        """Get the status of the indexer.

        :param name: The name of the indexer to fetch the status.
        :type name: str

        :return: SearchIndexerStatus
        :rtype: SearchIndexerStatus

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexer_operations.py
                :start-after: [START get_indexer_status]
                :end-before: [END get_indexer_status]
                :language: python
                :dedent: 4
                :caption: Get a SearchIndexer's status
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return self._client.indexers.get_status(name, **kwargs)
