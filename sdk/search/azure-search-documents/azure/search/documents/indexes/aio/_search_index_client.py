# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING, Union

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.async_paging import AsyncItemPaged
from .._generated.aio import SearchClient as _SearchServiceClient
from ...aio._search_client_async import SearchClient
from ...aio._utils_async import get_async_authentication_policy
from .._utils import (
    get_access_conditions,
    normalize_endpoint,
)
from ..._api_versions import DEFAULT_VERSION
from ..._headers_mixin import HeadersMixin
from ..._version import SDK_MONIKER
from ..models import (
    SearchIndex,
    SynonymMap,
)

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from .._generated.models import AnalyzeResult
    from ..models._models import AnalyzeTextOptions
    from typing import Any, Dict, List
    from azure.core.credentials_async import AsyncTokenCredential


class SearchIndexClient(HeadersMixin):
    """A client to interact with Azure search service Indexes.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str api_version: The Search API version to use for requests.

    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        **kwargs
    ) -> None:
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._endpoint = normalize_endpoint(endpoint)  # type: str
        self._credential = credential
        if isinstance(credential, AzureKeyCredential):
            self._aad = False
            self._client = _SearchServiceClient(
                endpoint=endpoint,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )  # type: _SearchServiceClient
        else:
            self._aad = True
            authentication_policy = get_async_authentication_policy(credential)
            self._client = _SearchServiceClient(
                endpoint=endpoint,
                authentication_policy=authentication_policy,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )  # type: _SearchServiceClient

    async def __aenter__(self):
        # type: () -> SearchIndexesClient
        await self._client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        return await self._client.__aexit__(*args)  # pylint:disable=no-member

    async def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.indexes.aio.SearchIndexClient` session."""
        return await self._client.close()

    def get_search_client(self, index_name, **kwargs):
        # type: (str, dict) -> SearchClient
        """Return a client to perform operations on Search.

        :param index_name: The name of the Search Index
        :type index_name: str
        :rtype: ~azure.search.documents.aio.SearchClient
        """
        return SearchClient(self._endpoint, index_name, self._credential, **kwargs)

    @distributed_trace
    def list_indexes(self, **kwargs):
        # type: (**Any) -> AsyncItemPaged[SearchIndex]
        """List the indexes in an Azure Search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
         list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: list[str]
        :return: List of indexes
        :rtype: ~azure.core.async_paging.AsyncItemPaged[:class:`~azure.search.documents.indexes.models.SearchIndex`]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if kwargs.get('select', None):
            kwargs['select'] = ','.join(kwargs['select'])
        # pylint:disable=protected-access
        return self._client.indexes.list(
            cls=lambda objs: [SearchIndex._from_generated(x) for x in objs], **kwargs
        )

    @distributed_trace
    def list_index_names(self, **kwargs):
        # type: (**Any) -> AsyncItemPaged[str]
        """List the index names in an Azure Search service.

        :return: List of index names
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        return self._client.indexes.list(
            cls=lambda objs: [x.name for x in objs], **kwargs
        )

    @distributed_trace_async
    async def get_index(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndex
        """

        :param name: The name of the index to retrieve.
        :type name: str
        :return: SearchIndex object
        :rtype: :class:`~azure.search.documents.indexes.models.SearchIndex`
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_index_crud_operations_async.py
                :start-after: [START get_index_async]
                :end-before: [END get_index_async]
                :language: python
                :dedent: 4
                :caption: Get an index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexes.get(name, **kwargs)
        return SearchIndex._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace_async
    async def get_index_statistics(self, index_name, **kwargs):
        # type: (str, **Any) -> dict
        """Returns statistics for the given index, including a document count
        and storage usage.

        :param index_name: The name of the index to retrieve.
        :type index_name: str
        :return: Statistics for the given index, including a document count and storage usage.
        :rtype: dict
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexes.get_statistics(index_name, **kwargs)
        return result.as_dict()

    @distributed_trace_async
    async def delete_index(self, index, **kwargs):
        # type: (Union[str, SearchIndex], **Any) -> None
        """Deletes a search index and all the documents it contains. The model must be
        provided instead of the name to use the access conditions

        :param index: The index to retrieve.
        :type index: str or :class:`~azure.search.documents.indexes.models.SearchIndex`
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_index_crud_operations_async.py
                :start-after: [START delete_index_async]
                :end-before: [END delete_index_async]
                :language: python
                :dedent: 4
                :caption: Delete an index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            index, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        try:
            index_name = index.name
        except AttributeError:
            index_name = index
        await self._client.indexes.delete(
            index_name=index_name, error_map=error_map, **kwargs
        )

    @distributed_trace_async
    async def create_index(self, index, **kwargs):
        # type: (SearchIndex, **Any) -> SearchIndex
        """Creates a new search index.

        :param index: The index object.
        :type index: :class:`~azure.search.documents.indexes.models.SearchIndex`
        :return: The index created
        :rtype: :class:`~azure.search.documents.indexes.models.SearchIndex`
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_index_crud_operations_async.py
                :start-after: [START create_index_async]
                :end-before: [END create_index_async]
                :language: python
                :dedent: 4
                :caption: Creating a new index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        patched_index = index._to_generated()  # pylint:disable=protected-access
        result = await self._client.indexes.create(patched_index, **kwargs)
        return result

    @distributed_trace_async
    async def create_or_update_index(self, index, allow_index_downtime=None, **kwargs):
        # type: (SearchIndex, bool, MatchConditions, **Any) -> SearchIndex
        """Creates a new search index or updates an index if it already exists.

        :param index: The index object.
        :type index: :class:`~azure.search.documents.indexes.models.SearchIndex`
        :param allow_index_downtime: Allows new analyzers, tokenizers, token filters, or char filters
         to be added to an index by taking the index offline for at least a few seconds. This
         temporarily causes indexing and query requests to fail. Performance and write availability of
         the index can be impaired for several minutes after the index is updated, or longer for very
         large indexes.
        :type allow_index_downtime: bool
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The index created or updated
        :rtype: :class:`~azure.search.documents.indexes.models.SearchIndex`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`, \
        :class:`~azure.core.exceptions.ResourceModifiedError`, \
        :class:`~azure.core.exceptions.ResourceNotModifiedError`, \
        :class:`~azure.core.exceptions.ResourceNotFoundError`, \
        :class:`~azure.core.exceptions.ResourceExistsError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_index_crud_operations_async.py
                :start-after: [START update_index_async]
                :end-before: [END update_index_async]
                :language: python
                :dedent: 4
                :caption: Update an index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            index, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        patched_index = index._to_generated()  # pylint:disable=protected-access
        result = await self._client.indexes.create_or_update(
            index_name=index.name,
            index=patched_index,
            allow_index_downtime=allow_index_downtime,
            error_map=error_map,
            **kwargs
        )
        return result

    @distributed_trace_async
    async def analyze_text(self, index_name, analyze_request, **kwargs):
        # type: (str, AnalyzeTextOptions, **Any) -> AnalyzeResult
        """Shows how an analyzer breaks text into tokens.

        :param index_name: The name of the index for which to test an analyzer.
        :type index_name: str
        :param analyze_request: The text and analyzer or analysis components to test.
        :type analyze_request: ~azure.search.documents.indexes.models.AnalyzeTextOptions
        :return: AnalyzeResult
        :rtype: ~azure.search.documents.indexes.models.AnalyzeRequest
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_analyze_text_async.py
                :start-after: [START simple_analyze_text_async]
                :end-before: [END simple_analyze_text_async]
                :language: python
                :dedent: 4
                :caption: Analyze text
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexes.analyze(
            index_name=index_name,
            request=analyze_request._to_analyze_request(),  # pylint:disable=protected-access
            **kwargs
        )
        return result

    @distributed_trace_async
    async def get_synonym_maps(self, **kwargs):
        # type: (**Any) -> List[SynonymMap]
        """List the Synonym Maps in an Azure Search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
         list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: list[str]
        :return: List of synonym maps
        :rtype: list[~azure.search.documents.indexes.models.SynonymMap]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_synonym_map_operations_async.py
                :start-after: [START get_synonym_maps_async]
                :end-before: [END get_synonym_maps_async]
                :language: python
                :dedent: 4
                :caption: List Synonym Maps

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if kwargs.get('select', None):
            kwargs['select'] = ','.join(kwargs['select'])
        result = await self._client.synonym_maps.list(**kwargs)
        # pylint:disable=protected-access
        return [SynonymMap._from_generated(x) for x in result.synonym_maps]

    @distributed_trace_async
    async def get_synonym_map_names(self, **kwargs):
        # type: (**Any) -> List[str]
        """List the Synonym Map names in an Azure Search service.

        :return: List of synonym map names
        :rtype: list[str]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.synonym_maps.list(**kwargs)
        return [x.name for x in result.synonym_maps]

    @distributed_trace_async
    async def get_synonym_map(self, name, **kwargs):
        # type: (str, **Any) -> SynonymMap
        """Retrieve a named Synonym Map in an Azure Search service

        :param name: The name of the Synonym Map to get
        :type name: str
        :return: The retrieved Synonym Map
        :rtype: :class:`~azure.search.documents.indexes.models.SynonymMap`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_synonym_map_operations_async.py
                :start-after: [START get_synonym_map_async]
                :end-before: [END get_synonym_map_async]
                :language: python
                :dedent: 4
                :caption: Get a Synonym Map

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.synonym_maps.get(name, **kwargs)
        return SynonymMap._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace_async
    async def delete_synonym_map(self, synonym_map, **kwargs):
        # type: (Union[str, SynonymMap], **Any) -> None
        """Delete a named Synonym Map in an Azure Search service. To use access conditions,
        the SynonymMap model must be provided instead of the name. It is enough to provide
        the name of the synonym map to delete unconditionally.

        :param name: The Synonym Map to delete
        :type name: str or ~azure.search.documents.indexes.models.SynonymMap
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None


        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_synonym_map_operations_async.py
                :start-after: [START delete_synonym_map_async]
                :end-before: [END delete_synonym_map_async]
                :language: python
                :dedent: 4
                :caption: Delete a Synonym Map

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            synonym_map, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        try:
            name = synonym_map.name
        except AttributeError:
            name = synonym_map
        await self._client.synonym_maps.delete(
            synonym_map_name=name, error_map=error_map, **kwargs
        )

    @distributed_trace_async
    async def create_synonym_map(self, synonym_map, **kwargs):
        # type: (SynonymMap, **Any) -> SynonymMap
        """Create a new Synonym Map in an Azure Search service

        :param synonym_map: The Synonym Map object
        :type synonym_map: :class:`~azure.search.documents.indexes.models.SynonymMap`
        :return: The created Synonym Map
        :rtype: :class:`~azure.search.documents.indexes.models.SynonymMap`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_synonym_map_operations_async.py
                :start-after: [START create_synonym_map_async]
                :end-before: [END create_synonym_map_async]
                :language: python
                :dedent: 4
                :caption: Create a Synonym Map

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        patched_synonym_map = (
            synonym_map._to_generated()  # pylint:disable=protected-access
        )
        result = await self._client.synonym_maps.create(patched_synonym_map, **kwargs)
        return SynonymMap._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace_async
    async def create_or_update_synonym_map(self, synonym_map, **kwargs):
        # type: (SynonymMap, **Any) -> SynonymMap
        """Create a new Synonym Map in an Azure Search service, or update an
        existing one.

        :param synonym_map: The Synonym Map object
        :type synonym_map: :class:`~azure.search.documents.indexes.models.SynonymMap`
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The created or updated Synonym Map
        :rtype: :class:`~azure.search.documents.indexes.models.SynonymMap`

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            synonym_map, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        patched_synonym_map = (
            synonym_map._to_generated()  # pylint:disable=protected-access
        )
        result = await self._client.synonym_maps.create_or_update(
            synonym_map_name=synonym_map.name,
            synonym_map=patched_synonym_map,
            error_map=error_map,
            **kwargs
        )
        return SynonymMap._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace_async
    async def get_service_statistics(self, **kwargs):
        # type: (**Any) -> dict
        """Get service level statistics for a search service."""
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.get_service_statistics(**kwargs)
        return result.as_dict()
