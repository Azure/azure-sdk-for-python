# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING, Union

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.aio import SearchClient as _SearchServiceClient
from ..models import SearchIndexerSkillset
from .._utils import (
    get_access_conditions,
    normalize_endpoint,
)
from ..models import (
    SearchIndexerDataSourceConnection,
)
from ..._api_versions import DEFAULT_VERSION
from ..._headers_mixin import HeadersMixin
from ..._version import SDK_MONIKER
from ...aio._utils_async import get_async_authentication_policy

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from .._generated.models import SearchIndexer, SearchIndexerStatus, DocumentKeysOrIds
    from typing import Any, Optional, Sequence
    from azure.core.credentials_async import AsyncTokenCredential


class SearchIndexerClient(HeadersMixin):  # pylint: disable=R0904
    """A client to interact with Azure search service Indexers.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str api_version: The Search API version to use for requests.
    :keyword str audience: sets the Audience to use for authentication with Azure Active Directory (AAD). The
     audience is not considered when using a shared key. If audience is not provided, the public cloud audience
     will be assumed.
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
        audience = kwargs.pop("audience", None)
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
            authentication_policy = get_async_authentication_policy(credential, audience=audience, is_async=True)
            self._client = _SearchServiceClient(
                endpoint=endpoint,
                authentication_policy=authentication_policy,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )  # type: _SearchServiceClient

    async def __aenter__(self):
        # type: () -> SearchIndexersClient
        await self._client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        return await self._client.__aexit__(*args)  # pylint:disable=no-member

    async def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.indexes.aio.SearchIndexerClient` session."""
        return await self._client.close()

    @distributed_trace_async
    async def create_indexer(self, indexer, **kwargs):
        # type: (SearchIndexer, **Any) -> SearchIndexer
        """Creates a new SearchIndexer.

        :param indexer: The definition of the indexer to create.
        :type indexer: ~azure.search.documents.indexes.models.SearchIndexer
        :return: The created SearchIndexer
        :rtype: ~azure.search.documents.indexes.models.SearchIndexer

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_indexer_operations_async.py
                :start-after: [START create_indexer_async]
                :end-before: [END create_indexer_async]
                :language: python
                :dedent: 4
                :caption: Create a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexers.create(indexer, **kwargs)
        return result

    @distributed_trace_async
    async def create_or_update_indexer(self, indexer, **kwargs):
        # type: (SearchIndexer, **Any) -> SearchIndexer
        """Creates a new indexer or updates a indexer if it already exists.

        :param indexer: The definition of the indexer to create or update.
        :type indexer: ~azure.search.documents.indexes.models.SearchIndexer
        :keyword skip_indexer_reset_requirement_for_cache: Ignores cache reset requirements.
        :paramtype skip_indexer_reset_requirement_for_cache: bool
        :keyword disable_cache_reprocessing_change_detection: Disables cache reprocessing change
         detection.
        :paramtype disable_cache_reprocessing_change_detection: bool
        :return: The created SearchIndexer
        :rtype: ~azure.search.documents.indexes.models.SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            indexer, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        name = indexer.name
        result = await self._client.indexers.create_or_update(
            indexer_name=name, indexer=indexer, error_map=error_map, **kwargs
        )
        return result

    @distributed_trace_async
    async def get_indexer(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndexer
        """Retrieves a indexer definition.

        :param name: The name of the indexer to retrieve.
        :type name: str
        :return: The SearchIndexer that is fetched.
        :rtype: ~azure.search.documents.indexes.models.SearchIndexer

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_indexer_operations_async.py
                :start-after: [START get_indexer_async]
                :end-before: [END get_indexer_async]
                :language: python
                :dedent: 4
                :caption: Retrieve a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexers.get(name, **kwargs)
        return result

    @distributed_trace_async
    async def get_indexers(self, **kwargs):
        # type: (**Any) -> Sequence[SearchIndexer]
        """Lists all indexers available for a search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
         list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: list[str]
        :return: List of all the SearchIndexers.
        :rtype: `list[~azure.search.documents.indexes.models.SearchIndexer]`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_indexer_operations_async.py
                :start-after: [START list_indexer_async]
                :end-before: [END list_indexer_async]
                :language: python
                :dedent: 4
                :caption: List all the SearchIndexers
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if kwargs.get('select', None):
            kwargs['select'] = ','.join(kwargs['select'])
        result = await self._client.indexers.list(**kwargs)
        return result.indexers

    @distributed_trace_async
    async def get_indexer_names(self, **kwargs):
        # type: (**Any) -> Sequence[str]
        """Lists all indexer names available for a search service.

        :return: List of all the SearchIndexer names.
        :rtype: `list[str]`

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexers.list(**kwargs)
        return [x.name for x in result.indexers]

    @distributed_trace_async
    async def delete_indexer(self, indexer, **kwargs):
        # type: (Union[str, SearchIndexer], **Any) -> None
        """Deletes an indexer. To use access conditions, the SearchIndexer model
        must be provided instead of the name. It is enough to provide
        the name of the indexer to delete unconditionally.

        :param name: The name or the indexer object to delete.
        :type name: str or ~azure.search.documents.indexes.models.SearchIndexer
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_indexer_operations_async.py
                :start-after: [START delete_indexer_async]
                :end-before: [END delete_indexer_async]
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
        await self._client.indexers.delete(name, error_map=error_map, **kwargs)

    @distributed_trace_async
    async def run_indexer(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Run an indexer.

        :param name: The name of the indexer to run.
        :type name: str

        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_indexer_operations_async.py
                :start-after: [START run_indexer_async]
                :end-before: [END run_indexer_async]
                :language: python
                :dedent: 4
                :caption: Run a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        await self._client.indexers.run(name, **kwargs)

    @distributed_trace_async
    async def reset_indexer(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Resets the change tracking state associated with an indexer.

        :param name: The name of the indexer to reset.
        :type name: str

        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_indexer_operations_async.py
                :start-after: [START reset_indexer_async]
                :end-before: [END reset_indexer_async]
                :language: python
                :dedent: 4
                :caption: Reset a SearchIndexer's change tracking state
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        await self._client.indexers.reset(name, **kwargs)

    @distributed_trace_async
    async def reset_documents(self, indexer, keys_or_ids, **kwargs):
        # type: (Union[str, SearchIndexer], DocumentKeysOrIds, **Any) -> None
        """Resets specific documents in the datasource to be selectively re-ingested by the indexer.

        :param indexer: The indexer to reset documents for.
        :type indexer: str or ~azure.search.documents.indexes.models.SearchIndexer
        :param keys_or_ids:
        :type keys_or_ids: ~azure.search.documents.indexes.models.DocumentKeysOrIds
        :return: None, or the result of cls(response)
        :keyword overwrite: If false, keys or ids will be appended to existing ones. If true, only the
         keys or ids in this payload will be queued to be re-ingested. The default is false.
        :paramtype overwrite: bool
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        kwargs["keys_or_ids"] = keys_or_ids
        try:
            name = indexer.name
        except AttributeError:
            name = indexer
        result = await self._client.indexers.reset_docs(name, **kwargs)
        return result

    @distributed_trace_async
    async def get_indexer_status(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndexerStatus
        """Get the status of the indexer.

        :param name: The name of the indexer to fetch the status.
        :type name: str

        :return: SearchIndexerStatus
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerStatus

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_indexer_operations_async.py
                :start-after: [START get_indexer_status_async]
                :end-before: [END get_indexer_status_async]
                :language: python
                :dedent: 4
                :caption: Get a SearchIndexer's status
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return await self._client.indexers.get_status(name, **kwargs)

    @distributed_trace_async
    async def create_data_source_connection(self, data_source_connection, **kwargs):
        # type: (SearchIndexerDataSourceConnection, **Any) -> SearchIndexerDataSourceConnection
        """Creates a new data source connection.
        :param data_source_connection: The definition of the data source connection to create.
        :type data_source_connection: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :return: The created SearchIndexerDataSourceConnection
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START create_data_source_connection_async]
                :end-before: [END create_data_source_connection_async]
                :language: python
                :dedent: 4
                :caption: Create a SearchIndexerDataSourceConnection
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        # pylint:disable=protected-access
        packed_data_source = data_source_connection._to_generated()
        result = await self._client.data_sources.create(packed_data_source, **kwargs)
        return SearchIndexerDataSourceConnection._from_generated(result)

    @distributed_trace_async
    async def create_or_update_data_source_connection(
        self, data_source_connection, **kwargs
    ):
        # type: (SearchIndexerDataSourceConnection, **Any) -> SearchIndexerDataSourceConnection
        """Creates a new data source connection or updates a data source connection if it already exists.
        :param data_source_connection: The definition of the data source connection to create or update.
        :type data_source_connection: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword skip_indexer_reset_requirement_for_cache: Ignores cache reset requirements.
        :paramtype skip_indexer_reset_requirement_for_cache: bool
        :return: The created SearchIndexerDataSourceConnection
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            data_source_connection,
            kwargs.pop("match_condition", MatchConditions.Unconditionally),
        )
        kwargs.update(access_condition)
        name = data_source_connection.name
        # pylint:disable=protected-access
        packed_data_source = data_source_connection._to_generated()
        result = await self._client.data_sources.create_or_update(
            data_source_name=name,
            data_source=packed_data_source,
            error_map=error_map,
            **kwargs
        )
        return SearchIndexerDataSourceConnection._from_generated(result)

    @distributed_trace_async
    async def delete_data_source_connection(self, data_source_connection, **kwargs):
        # type: (Union[str, SearchIndexerDataSourceConnection], **Any) -> None
        """Deletes a data source connection. To use access conditions, the
        SearchIndexerDataSourceConnection model must be provided instead of the name.
        It is enough to provide the name of the data source connection to delete unconditionally

        :param data_source_connection: The data source connection to delete.
        :type data_source_connection: str or ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START delete_data_source_async]
                :end-before: [END delete_data_source_async]
                :language: python
                :dedent: 4
                :caption: Delete a SearchIndexerDataSourceConnection
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            data_source_connection,
            kwargs.pop("match_condition", MatchConditions.Unconditionally),
        )
        kwargs.update(access_condition)
        try:
            name = data_source_connection.name
        except AttributeError:
            name = data_source_connection
        await self._client.data_sources.delete(
            data_source_name=name, error_map=error_map, **kwargs
        )

    @distributed_trace_async
    async def get_data_source_connection(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndexerDataSourceConnection
        """Retrieves a data source connection definition.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
         list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: list[str]
        :param name: The name of the data source connection to retrieve.
        :type name: str
        :return: The SearchIndexerDataSourceConnection that is fetched.
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START get_data_source_connection_async]
                :end-before: [END get_data_source_connection_async]
                :language: python
                :dedent: 4
                :caption: Retrieve a SearchIndexerDataSourceConnection
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if kwargs.get('select', None):
            kwargs['select'] = ','.join(kwargs['select'])
        result = await self._client.data_sources.get(name, **kwargs)
        # pylint:disable=protected-access
        return SearchIndexerDataSourceConnection._from_generated(result)

    @distributed_trace_async
    async def get_data_source_connections(self, **kwargs):
        # type: (**Any) -> Sequence[SearchIndexerDataSourceConnection]
        """Lists all data source connections available for a search service.

        :return: List of all the data source connections.
        :rtype: `list[~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection]`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START list_data_source_connection_async]
                :end-before: [END list_data_source_connection_async]
                :language: python
                :dedent: 4
                :caption: List all SearchIndexerDataSourceConnections
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.data_sources.list(**kwargs)
        # pylint:disable=protected-access
        return [
            SearchIndexerDataSourceConnection._from_generated(x)
            for x in result.data_sources
        ]

    @distributed_trace_async
    async def get_data_source_connection_names(self, **kwargs):
        # type: (**Any) -> Sequence[str]
        """Lists all data source connection names available for a search service.

        :return: List of all the data source connection names.
        :rtype: `list[str]`

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.data_sources.list(**kwargs)
        return [x.name for x in result.data_sources]

    @distributed_trace_async
    async def get_skillsets(self, **kwargs):
        # type: (**Any) -> List[SearchIndexerSkillset]
        """List the SearchIndexerSkillsets in an Azure Search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
         list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: list[str]
        :return: List of SearchIndexerSkillsets
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexerSkillset]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_skillset_operations_async.py
                :start-after: [START get_skillsets]
                :end-before: [END get_skillsets]
                :language: python
                :dedent: 4
                :caption: List SearchIndexerSkillsets

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if kwargs.get('select', None):
            kwargs['select'] = ','.join(kwargs['select'])
        result = await self._client.skillsets.list(**kwargs)
        return [SearchIndexerSkillset._from_generated(skillset) for skillset in result.skillsets] # pylint:disable=protected-access

    @distributed_trace_async
    async def get_skillset_names(self, **kwargs):
        # type: (**Any) -> List[str]
        """List the SearchIndexerSkillset names in an Azure Search service.

        :return: List of SearchIndexerSkillset names
        :rtype: list[str]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.skillsets.list(**kwargs)
        return [x.name for x in result.skillsets]

    @distributed_trace_async
    async def get_skillset(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndexerSkillset
        """Retrieve a named SearchIndexerSkillset in an Azure Search service

        :param name: The name of the SearchIndexerSkillset to get
        :type name: str
        :return: The retrieved SearchIndexerSkillset
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_skillset_operations_async.py
                :start-after: [START get_skillset]
                :end-before: [END get_skillset]
                :language: python
                :dedent: 4
                :caption: Get a SearchIndexerSkillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.skillsets.get(name, **kwargs)
        return SearchIndexerSkillset._from_generated(result) # pylint:disable=protected-access

    @distributed_trace_async
    async def delete_skillset(self, skillset, **kwargs):
        # type: (Union[str, SearchIndexerSkillset], **Any) -> None
        """Delete a named SearchIndexerSkillset in an Azure Search service. To use access conditions,
        the SearchIndexerSkillset model must be provided instead of the name. It is enough to provide
        the name of the skillset to delete unconditionally

        :param skillset: The SearchIndexerSkillset to delete
        :type skillset: str or ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_skillset_operations_async.py
                :start-after: [START delete_skillset]
                :end-before: [END delete_skillset]
                :language: python
                :dedent: 4
                :caption: Delete a SearchIndexerSkillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            skillset, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        try:
            name = skillset.name
        except AttributeError:
            name = skillset
        await self._client.skillsets.delete(name, error_map=error_map, **kwargs)

    @distributed_trace_async
    async def create_skillset(self, skillset, **kwargs):
        # type: (SearchIndexerSkillset, **Any) -> SearchIndexerSkillset
        """Create a new SearchIndexerSkillset in an Azure Search service

        :param skillset: The SearchIndexerSkillset object to create
        :type skillset: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :return: The created SearchIndexerSkillset
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerSkillset

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_skillset_operations_async.py
                :start-after: [START create_skillset]
                :end-before: [END create_skillset]
                :language: python
                :dedent: 4
                :caption: Create a SearchIndexerSkillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        skillset = skillset._to_generated() if hasattr(skillset, '_to_generated') else skillset # pylint:disable=protected-access
        result = await self._client.skillsets.create(skillset, **kwargs)
        return SearchIndexerSkillset._from_generated(result) # pylint:disable=protected-access

    @distributed_trace_async
    async def create_or_update_skillset(self, skillset, **kwargs):
        # type: (SearchIndexerSkillset, **Any) -> SearchIndexerSkillset
        """Create a new SearchIndexerSkillset in an Azure Search service, or update an
        existing one.

        :param skillset: The SearchIndexerSkillset object to create or update
        :type skillset: :class:`~azure.search.documents.indexes.models.SearchIndexerSkillset`
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword skip_indexer_reset_requirement_for_cache: Ignores cache reset requirements.
        :paramtype skip_indexer_reset_requirement_for_cache: bool
        :keyword disable_cache_reprocessing_change_detection: Disables cache reprocessing change
         detection.
        :paramtype disable_cache_reprocessing_change_detection: bool
        :return: The created or updated SearchIndexerSkillset
        :rtype: :class:`~azure.search.documents.indexes.models.SearchIndexerSkillset`

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            skillset, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        skillset = skillset._to_generated() if hasattr(skillset, '_to_generated') else skillset # pylint:disable=protected-access

        result = await self._client.skillsets.create_or_update(
            skillset_name=skillset.name,
            skillset=skillset,
            error_map=error_map,
            **kwargs
        )
        return SearchIndexerSkillset._from_generated(result) # pylint:disable=protected-access

    @distributed_trace_async
    async def reset_skills(self, skillset, skill_names, **kwargs):
        # type: (Union[str, SearchIndexerSkillset], List[str], **Any) -> None
        """Reset an existing skillset in a search service.

        :param skillset: The SearchIndexerSkillset to reset
        :type skillset: str or ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :param skill_names: the names of skills to be reset.
        :type skill_names: list[str]
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        try:
            name = skillset.name
        except AttributeError:
            name = skillset
        result = await self._client.skillsets.reset_skills(name, skill_names, **kwargs)
        return result
