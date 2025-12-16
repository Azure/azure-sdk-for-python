# pylint: disable=too-many-lines,line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, cast, List, Sequence, Union, Optional, TYPE_CHECKING

from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ... import models as _models

if TYPE_CHECKING:
    from ....aio import SearchClient
from ._operations import (
    _SearchIndexClientOperationsMixin as _SearchIndexClientOperationsMixinGenerated,
    _SearchIndexerClientOperationsMixin as _SearchIndexerClientOperationsMixinGenerated,
)


class _SearchIndexClientOperationsMixin(_SearchIndexClientOperationsMixinGenerated):
    """Custom operations mixin for SearchIndexClient (async)."""

    @distributed_trace_async
    async def delete_synonym_map(
        self,
        synonym_map: Union[str, _models.SynonymMap],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> None:
        """Deletes a synonym map.

        :param synonym_map: The name of the synonym map to delete or a SynonymMap object. Required.
        :type synonym_map: str or ~azure.search.documents.indexes.models.SynonymMap
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = synonym_map.name  # type: ignore
            return await self._delete_synonym_map(
                name=name,
                match_condition=match_condition,
                etag=synonym_map.e_tag,  # type: ignore
                **kwargs,
            )
        except AttributeError:
            name = synonym_map  # type: ignore
            return await self._delete_synonym_map(
                name=name,
                **kwargs,
            )

    @distributed_trace_async
    async def create_or_update_synonym_map(
        self,
        synonym_map: _models.SynonymMap,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> _models.SynonymMap:
        """Creates a new synonym map or updates a synonym map if it already exists.

        :param synonym_map: The SynonymMap object to create or update. Required.
        :type synonym_map: ~azure.search.documents.indexes.models.SynonymMap
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: SynonymMap
        :rtype: ~azure.search.documents.indexes.models.SynonymMap
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._create_or_update_synonym_map(
            name=synonym_map.name,
            synonym_map=synonym_map,
            prefer="return=representation",
            match_condition=match_condition,
            etag=synonym_map.e_tag,
            **kwargs,
        )

    @distributed_trace_async
    async def delete_index(
        self,
        index: Union[str, _models.SearchIndex],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> None:
        """Deletes a search index and all the documents it contains.

        :param index: The name of the index to delete or a SearchIndex object. Required.
        :type index: str or ~azure.search.documents.indexes.models.SearchIndex
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = index.name  # type: ignore
            return await self._delete_index(
                name=name,
                match_condition=match_condition,
                etag=index.e_tag,  # type: ignore
                **kwargs,
            )
        except AttributeError:
            name = index  # type: ignore
            return await self._delete_index(
                name=name,
                **kwargs,
            )

    @distributed_trace_async
    async def create_or_update_index(
        self,
        index: _models.SearchIndex,
        allow_index_downtime: Optional[bool] = None,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> _models.SearchIndex:
        """Creates a new search index or updates an index if it already exists.

        :param index: The SearchIndex object to create or update. Required.
        :type index: ~azure.search.documents.indexes.models.SearchIndex
        :param allow_index_downtime: Allows new analyzers, tokenizers, token filters, or char filters
         to be added to an index by taking the index offline for at least a few seconds. This
         temporarily causes indexing and query requests to fail. Performance and write availability of
         the index can be impaired for several minutes after the index is updated, or longer for very
         large indexes. Default value is None.
        :type allow_index_downtime: bool
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: SearchIndex
        :rtype: ~azure.search.documents.indexes.models.SearchIndex
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._create_or_update_index(
            name=index.name,
            index=index,
            prefer="return=representation",
            allow_index_downtime=allow_index_downtime,
            match_condition=match_condition,
            etag=index.e_tag,
            **kwargs,
        )

    @distributed_trace_async
    async def create_or_update_alias(
        self,
        alias: _models.SearchAlias,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> _models.SearchAlias:
        """Creates a new search alias or updates an alias if it already exists.

        :param alias: The SearchAlias object to create or update. Required.
        :type alias: ~azure.search.documents.indexes.models.SearchAlias
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: SearchAlias
        :rtype: ~azure.search.documents.indexes.models.SearchAlias
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._create_or_update_alias(
            name=alias.name,
            alias=alias,
            prefer="return=representation",
            match_condition=match_condition,
            etag=alias.e_tag,
            **kwargs,
        )

    @distributed_trace_async
    async def delete_alias(
        self,
        alias: Union[str, _models.SearchAlias],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> None:
        """Deletes a search alias and its associated mapping to an index.

        :param alias: The name of the alias to delete or a SearchAlias object. Required.
        :type alias: str or ~azure.search.documents.indexes.models.SearchAlias
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = alias.name  # type: ignore
            return await self._delete_alias(
                name=name,
                match_condition=match_condition,
                etag=alias.e_tag,  # type: ignore
                **kwargs,
            )
        except AttributeError:
            name = alias  # type: ignore
            return await self._delete_alias(
                name=name,
                **kwargs,
            )

    @distributed_trace_async
    async def delete_knowledge_base(
        self,
        knowledge_base: Union[str, _models.KnowledgeBase],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> None:
        """Deletes a knowledge base.

        :param knowledge_base: The name of the knowledge base to delete or a KnowledgeBase object. Required.
        :type knowledge_base: str or ~azure.search.documents.indexes.models.KnowledgeBase
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = knowledge_base.name  # type: ignore
            return await self._delete_knowledge_base(
                name=name,
                match_condition=match_condition,
                etag=knowledge_base.e_tag,  # type: ignore
                **kwargs,
            )
        except AttributeError:
            name = knowledge_base  # type: ignore
            return await self._delete_knowledge_base(
                name=name,
                **kwargs,
            )

    @distributed_trace_async
    async def create_or_update_knowledge_base(
        self,
        knowledge_base: _models.KnowledgeBase,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> _models.KnowledgeBase:
        """Creates a new knowledge base or updates a knowledge base if it already exists.

        :param knowledge_base: The KnowledgeBase object to create or update. Required.
        :type knowledge_base: ~azure.search.documents.indexes.models.KnowledgeBase
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: KnowledgeBase
        :rtype: ~azure.search.documents.indexes.models.KnowledgeBase
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._create_or_update_knowledge_base(
            name=knowledge_base.name,
            knowledge_base=knowledge_base,
            prefer="return=representation",
            match_condition=match_condition,
            etag=knowledge_base.e_tag,
            **kwargs,
        )

    @distributed_trace_async
    async def create_or_update_knowledge_source(
        self,
        knowledge_source: _models.KnowledgeSource,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> _models.KnowledgeSource:
        """Creates a new knowledge source or updates a knowledge source if it already exists.

        :param knowledge_source: The KnowledgeSource object to create or update. Required.
        :type knowledge_source: ~azure.search.documents.indexes.models.KnowledgeSource
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: KnowledgeSource
        :rtype: ~azure.search.documents.indexes.models.KnowledgeSource
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._create_or_update_knowledge_source(
            name=knowledge_source.name,
            knowledge_source=knowledge_source,
            prefer="return=representation",
            match_condition=match_condition,
            etag=knowledge_source.e_tag,
            **kwargs,
        )

    @distributed_trace_async
    async def delete_knowledge_source(
        self,
        knowledge_source: Union[str, _models.KnowledgeSource],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> None:
        """Deletes a knowledge source.

        :param knowledge_source: The name of the knowledge source to delete or a KnowledgeSource object. Required.
        :type knowledge_source: str or ~azure.search.documents.indexes.models.KnowledgeSource
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = knowledge_source.name  # type: ignore
            return await self._delete_knowledge_source(
                name=name,
                match_condition=match_condition,
                etag=knowledge_source.e_tag,  # type: ignore
                **kwargs,
            )
        except AttributeError:
            name = knowledge_source  # type: ignore
            return await self._delete_knowledge_source(
                name=name,
                **kwargs,
            )

    @distributed_trace
    def list_index_names(self, **kwargs: Any) -> AsyncItemPaged[str]:
        """Lists the names of all indexes available for a search service.

        :return: An async iterator like instance of index names
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        names = self.list_indexes(cls=lambda objs: [x.name for x in objs], **kwargs)
        return cast(AsyncItemPaged[str], names)

    @distributed_trace_async
    async def get_synonym_maps(self, **kwargs: Any) -> List[_models.SynonymMap]:
        """Lists all synonym maps available for a search service.

        :return: List of synonym maps
        :rtype: list[~azure.search.documents.indexes.models.SynonymMap]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._get_synonym_maps(**kwargs)
        assert result.synonym_maps is not None  # Hint for mypy
        # typed_result = [cast(_models.SynonymMap, x) for x in result.synonym_maps]
        typed_result = result.synonym_maps
        return typed_result

    @distributed_trace_async
    async def get_synonym_map_names(self, **kwargs: Any) -> List[str]:
        """Lists the names of all synonym maps available for a search service.

        :return: List of synonym map names
        :rtype: list[str]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self.get_synonym_maps(**kwargs)
        return [x.name for x in result]

    @distributed_trace
    def list_alias_names(self, **kwargs) -> AsyncItemPaged[str]:
        """List the alias names in an Azure Search service.

        :return: List of alias names
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError: If the operation fails.
        """
        names = self.list_aliases(cls=lambda objs: [x.name for x in objs], **kwargs)
        return cast(AsyncItemPaged[str], names)

    @distributed_trace_async
    async def analyze_text(
        self,
        index_name: str,
        analyze_request: _models.AnalyzeTextOptions,
        **kwargs: Any,
    ) -> _models.AnalyzeResult:
        """Shows how an analyzer breaks text into tokens.

        :param index_name: The name of the index to test an analyzer on. Required.
        :type index_name: str
        :param analyze_request: The text and analyzer or analysis components to test. Required.
        :type analyze_request: ~azure.search.documents.indexes.models.AnalyzeTextOptions
        :return: AnalyzeResult
        :rtype: ~azure.search.documents.indexes.models.AnalyzeResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._analyze_text(
            name=index_name,
            request=analyze_request,
            **kwargs,
        )

    @distributed_trace_async
    async def get_index_statistics(
        self,
        index_name: str,
        **kwargs: Any,
    ) -> _models.GetIndexStatisticsResult:
        """Returns statistics for the given index, including a document count and storage usage.

        :param index_name: The name of the index to retrieve statistics for. Required.
        :type index_name: str
        :return: GetIndexStatisticsResult
        :rtype: ~azure.search.documents.indexes.models.GetIndexStatisticsResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._get_index_statistics(
            name=index_name,
            **kwargs,
        )

    def get_search_client(self, index_name: str, **kwargs: Any) -> "SearchClient":
        """Return a client to perform operations on Search.

        :param index_name: The name of the index. Required.
        :type index_name: str
        :return: A SearchClient for operations on the named index.
        :rtype: ~azure.search.documents.aio.SearchClient
        """
        # pylint: disable=import-outside-toplevel
        from ....aio import SearchClient

        return SearchClient(
            endpoint=self._config.endpoint,
            index_name=index_name,
            credential=self._config.credential,
            **kwargs,
        )


class _SearchIndexerClientOperationsMixin(_SearchIndexerClientOperationsMixinGenerated):
    """Custom operations mixin for SearchIndexerClient (async)."""

    @distributed_trace_async
    async def delete_data_source_connection(
        self,
        data_source_connection: Union[str, _models.SearchIndexerDataSourceConnection],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> None:
        """Deletes a data source connection.

        :param data_source_connection: The name of the data source connection to delete or a SearchIndexerDataSourceConnection object. Required.
        :type data_source_connection: str or ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = data_source_connection.name  # type: ignore
            return await self._delete_data_source_connection(
                name=name,
                match_condition=match_condition,
                etag=data_source_connection.e_tag,  # type: ignore
                **kwargs,
            )
        except AttributeError:
            name = data_source_connection  # type: ignore
            return await self._delete_data_source_connection(
                name=name,
                **kwargs,
            )

    @distributed_trace_async
    async def create_or_update_data_source_connection(
        self,
        data_source_connection: _models.SearchIndexerDataSourceConnection,
        *,
        skip_indexer_reset_requirement_for_cache: Optional[bool] = None,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> _models.SearchIndexerDataSourceConnection:
        """Creates a new data source connection or updates a data source connection if it already exists.

        :param data_source_connection: The SearchIndexerDataSourceConnection object to create or update. Required.
        :type data_source_connection: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :keyword skip_indexer_reset_requirement_for_cache: Ignores cache reset requirements. Default
         value is None.
        :paramtype skip_indexer_reset_requirement_for_cache: bool
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: SearchIndexerDataSourceConnection
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._create_or_update_data_source_connection(
            name=data_source_connection.name,
            data_source=data_source_connection,
            prefer="return=representation",
            match_condition=match_condition,
            etag=data_source_connection.e_tag,
            skip_indexer_reset_requirement_for_cache=skip_indexer_reset_requirement_for_cache,
            **kwargs,
        )

    @distributed_trace_async
    async def delete_indexer(
        self,
        indexer: Union[str, _models.SearchIndexer],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> None:
        """Deletes an indexer.

        :param indexer: The name of the indexer to delete or a SearchIndexer object. Required.
        :type indexer: str or ~azure.search.documents.indexes.models.SearchIndexer
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = indexer.name  # type: ignore
            return await self._delete_indexer(
                name=name,
                match_condition=match_condition,
                etag=indexer.e_tag,  # type: ignore
                **kwargs,
            )
        except AttributeError:
            name = indexer  # type: ignore
            return await self._delete_indexer(
                name=name,
                **kwargs,
            )

    @distributed_trace_async
    async def create_or_update_indexer(
        self,
        indexer: _models.SearchIndexer,
        *,
        skip_indexer_reset_requirement_for_cache: Optional[bool] = None,
        disable_cache_reprocessing_change_detection: Optional[bool] = None,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> _models.SearchIndexer:
        """Creates a new indexer or updates an indexer if it already exists.

        :param indexer: The SearchIndexer object to create or update. Required.
        :type indexer: ~azure.search.documents.indexes.models.SearchIndexer
        :keyword skip_indexer_reset_requirement_for_cache: Ignores cache reset requirements. Default
         value is None.
        :paramtype skip_indexer_reset_requirement_for_cache: bool
        :keyword disable_cache_reprocessing_change_detection: Disables cache reprocessing change
         detection. Default value is None.
        :paramtype disable_cache_reprocessing_change_detection: bool
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: SearchIndexer
        :rtype: ~azure.search.documents.indexes.models.SearchIndexer
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._create_or_update_indexer(
            name=indexer.name,
            indexer=indexer,
            prefer="return=representation",
            match_condition=match_condition,
            etag=indexer.e_tag,
            skip_indexer_reset_requirement_for_cache=skip_indexer_reset_requirement_for_cache,
            disable_cache_reprocessing_change_detection=disable_cache_reprocessing_change_detection,
            **kwargs,
        )

    @distributed_trace_async
    async def delete_skillset(
        self,
        skillset: Union[str, _models.SearchIndexerSkillset],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> None:
        """Deletes a skillset.

        :param skillset: The name of the skillset to delete or a SearchIndexerSkillset object. Required.
        :type skillset: str or ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = skillset.name  # type: ignore
            return await self._delete_skillset(
                name=name,
                match_condition=match_condition,
                etag=skillset.e_tag,  # type: ignore
                **kwargs,
            )
        except AttributeError:
            name = skillset  # type: ignore
            return await self._delete_skillset(
                name=name,
                **kwargs,
            )

    @distributed_trace_async
    async def create_or_update_skillset(
        self,
        skillset: _models.SearchIndexerSkillset,
        *,
        skip_indexer_reset_requirement_for_cache: Optional[bool] = None,
        disable_cache_reprocessing_change_detection: Optional[bool] = None,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any,
    ) -> _models.SearchIndexerSkillset:
        """Creates a new skillset in a search service or updates the skillset if it already exists.

        :param skillset: The SearchIndexerSkillset object to create or update. Required.
        :type skillset: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :keyword skip_indexer_reset_requirement_for_cache: Ignores cache reset requirements. Default
         value is None.
        :paramtype skip_indexer_reset_requirement_for_cache: bool
        :keyword disable_cache_reprocessing_change_detection: Disables cache reprocessing change
         detection. Default value is None.
        :paramtype disable_cache_reprocessing_change_detection: bool
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: SearchIndexerSkillset
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._create_or_update_skillset(
            name=skillset.name,
            skillset=skillset,
            prefer="return=representation",
            match_condition=match_condition,
            etag=skillset.e_tag,
            skip_indexer_reset_requirement_for_cache=skip_indexer_reset_requirement_for_cache,
            disable_cache_reprocessing_change_detection=disable_cache_reprocessing_change_detection,
            **kwargs,
        )

    @distributed_trace_async
    async def get_skillsets(
        self, *, select: Optional[str] = None, **kwargs: Any
    ) -> List[_models.SearchIndexerSkillset]:
        """Lists all skillsets available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a comma-separated
         list of JSON property names, or '*' for all properties. The default is all properties. Default
         value is None.
        :paramtype select: str
        :return: List of all the SearchIndexerSkillsets.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexerSkillset]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if select is not None:
            kwargs["select"] = ",".join(select)
        result = await self._get_skillsets(**kwargs)
        assert result.skillsets is not None  # Hint for mypy
        # typed_result = [cast(_models.SearchIndexerSkillset, x) for x in result.skillsets]
        typed_result = result.skillsets
        return typed_result

    @distributed_trace_async
    async def get_indexers(self, *, select: Optional[str] = None, **kwargs: Any) -> List[_models.SearchIndexer]:
        """Lists all indexers available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a comma-separated
         list of JSON property names, or '*' for all properties. The default is all properties. Default
         value is None.
        :paramtype select: str
        :return: List of all the SearchIndexers.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexer]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if select is not None:
            kwargs["select"] = ",".join(select)
        result = await self._get_indexers(**kwargs)
        assert result.indexers is not None  # Hint for mypy
        # typed_result = [cast(_models.SearchIndexer, x) for x in result.indexers]
        typed_result = result.indexers
        return typed_result

    @distributed_trace_async
    async def get_indexer_names(self, **kwargs) -> Sequence[str]:
        """Lists all indexer names available for a search service.

        :return: List of all the SearchIndexer names.
        :rtype: list[str]
        """
        result = await self.get_indexers(**kwargs)
        return [x.name for x in result]

    @distributed_trace_async
    async def get_data_source_connections(
        self, *, select: Optional[str] = None, **kwargs: Any
    ) -> List[_models.SearchIndexerDataSourceConnection]:
        """Lists all data source connections available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a comma-separated
         list of JSON property names, or '*' for all properties. The default is all properties. Default
         value is None.
        :paramtype select: str
        :return: List of all the data source connections.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if select is not None:
            kwargs["select"] = ",".join(select)
        result = await self._get_data_source_connections(**kwargs)
        assert result.data_sources is not None  # Hint for mypy
        # typed_result = [cast(_models.SearchIndexerDataSourceConnection, x) for x in result.data_sources]
        typed_result = result.data_sources
        return typed_result

    @distributed_trace_async
    async def get_data_source_connection_names(self, **kwargs) -> Sequence[str]:
        """Lists all data source connection names available for a search service.

        :return: List of all the data source connection names.
        :rtype: list[str]

        """
        result = await self.get_data_source_connections(**kwargs)
        return [x.name for x in result]

    @distributed_trace_async
    async def get_skillset_names(self, **kwargs) -> Sequence[str]:
        """List the SearchIndexerSkillset names in an Azure Search service.

        :return: List of SearchIndexerSkillset names
        :rtype: list[str]
        :raises ~azure.core.exceptions.HttpResponseError: If there is an error in the REST request.

        """
        result = await self.get_skillsets(**kwargs)
        return [x.name for x in result]

    @distributed_trace_async
    async def reset_documents(
        self,
        indexer: Union[str, _models.SearchIndexer],
        keys_or_ids: _models.DocumentKeysOrIds,
        *,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        """Resets specific documents in the datasource to be selectively re-ingested by the indexer.

        :param indexer: The indexer to reset documents for. Can be the indexer name or a SearchIndexer object.
        :type indexer: str or ~azure.search.documents.indexes.models.SearchIndexer
        :param keys_or_ids: The document keys or ids to reset.
        :type keys_or_ids: ~azure.search.documents.indexes.models.DocumentKeysOrIds
        :keyword overwrite: If false, keys or ids will be appended to existing ones. If true, only the
         keys or ids in this payload will be queued to be re-ingested. Default value is False.
        :paramtype overwrite: bool
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = indexer.name  # type: ignore
        except AttributeError:
            name = indexer  # type: ignore
        return await self._reset_documents(
            name=name,
            keys_or_ids=keys_or_ids,
            overwrite=overwrite,
            **kwargs,
        )

    @distributed_trace_async
    async def reset_skills(
        self,
        skillset: Union[str, _models.SearchIndexerSkillset],
        skill_names: List[str],
        **kwargs: Any,
    ) -> None:
        """Reset an existing skillset in a search service.

        :param skillset: The skillset to reset skills for. Can be the skillset name or a SearchIndexerSkillset object.
        :type skillset: str or ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :param skill_names: The names of the skills to reset.
        :type skill_names: list[str]
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = skillset.name  # type: ignore
        except AttributeError:
            name = skillset  # type: ignore
        return await self._reset_skills(
            name=name,
            skill_names=_models.SkillNames(skill_names=skill_names),
            **kwargs,
        )

    @distributed_trace_async
    async def resync(
        self,
        indexer: Union[str, _models.SearchIndexer],
        indexer_resync_options: List[Union[str, _models.IndexerResyncOption]],
        **kwargs: Any,
    ) -> None:
        """Resync selective options from the datasource to be re-ingested by the indexer.

        :param indexer: The indexer to resync. Can be the indexer name or a SearchIndexer object.
        :type indexer: str or ~azure.search.documents.indexes.models.SearchIndexer
        :param indexer_resync_options: Re-sync options that have been pre-defined from data source.
        :type indexer_resync_options: list[str or ~azure.search.documents.indexes.models.IndexerResyncOption]
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        try:
            name: str = indexer.name  # type: ignore
        except AttributeError:
            name = indexer  # type: ignore
        indexer_resync = _models.IndexerResyncBody(options=indexer_resync_options)
        return await self._resync(
            name=name,
            indexer_resync=indexer_resync,
            **kwargs,
        )


__all__: list[str] = [
    "_SearchIndexClientOperationsMixin",
    "_SearchIndexerClientOperationsMixin",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
