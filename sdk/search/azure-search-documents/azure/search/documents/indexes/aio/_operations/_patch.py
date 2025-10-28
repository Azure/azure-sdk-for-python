# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, AsyncIterator, cast, List, Sequence, Union, overload

from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ... import models as _models
from ._operations import (
    _SearchIndexClientOperationsMixin as _SearchIndexClientOperationsMixinGenerated,
    _SearchIndexerClientOperationsMixin as _SearchIndexerClientOperationsMixinGenerated,
)


class _SearchIndexClientOperationsMixin(_SearchIndexClientOperationsMixinGenerated):
    """Custom operations mixin for SearchIndexClient (async)."""

    @overload
    async def delete_synonym_map(
        self,
        synonym_map_name: str,
        *,
        etag: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a synonym map.

        :param synonym_map_name: The name of the synonym map to delete. Required.
        :type synonym_map_name: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    async def delete_synonym_map(
        self,
        synonym_map: _models.SynonymMap,
        /,
        *,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a synonym map.

        :param synonym_map: The SynonymMap object to delete. Required.
        :type synonym_map: ~azure.search.documents.indexes.models.SynonymMap
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def delete_synonym_map(self, *args: Union[str, _models.SynonymMap], **kwargs: Any) -> None:
        """Deletes a synonym map.

        :param synonym_map_name: The name of the synonym map to delete. Required.
        :type synonym_map_name: str
        :param synonym_map: The SynonymMap object to delete.
        :type synonym_map: ~azure.search.documents.indexes.models.SynonymMap
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if args and isinstance(args[0], _models.SynonymMap):
            synonym_map = args[0]
            kwargs.setdefault("etag", synonym_map.e_tag)
            return await super().delete_synonym_map(synonym_map.name, **kwargs)
        else:
            return await super().delete_synonym_map(*args, **kwargs)

    @overload
    async def delete_index(
        self,
        index_name: str,
        *,
        query_source_authorization: str | None = None,
        etag: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a search index and all the documents it contains.

        :param index_name: The name of the index to delete. Required.
        :type index_name: str
        :keyword query_source_authorization: Token identifying the user for which the query is being
         executed. This token is used to enforce security restrictions on documents. Default value is
         None.
        :paramtype query_source_authorization: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    async def delete_index(
        self,
        index: _models.SearchIndex,
        /,
        *,
        query_source_authorization: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a search index and all the documents it contains.

        :param index: The SearchIndex object to delete. Required.
        :type index: ~azure.search.documents.indexes.models.SearchIndex
        :keyword query_source_authorization: Token identifying the user for which the query is being
         executed. This token is used to enforce security restrictions on documents. Default value is
         None.
        :paramtype query_source_authorization: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def delete_index(self, *args: Union[str, _models.SearchIndex], **kwargs: Any) -> None:
        """Deletes a search index and all the documents it contains.

        :param index_name: The name of the index to delete. Required.
        :type index_name: str
        :param index: The SearchIndex object to delete.
        :type index: ~azure.search.documents.indexes.models.SearchIndex
        :keyword query_source_authorization: Token identifying the user for which the query is being
         executed. This token is used to enforce security restrictions on documents. Default value is
         None.
        :paramtype query_source_authorization: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if args and isinstance(args[0], _models.SearchIndex):
            index = args[0]
            kwargs.setdefault("etag", index.e_tag)
            return await super().delete_index(index.name, **kwargs)
        else:
            return await super().delete_index(*args, **kwargs)

    @overload
    async def delete_alias(
        self,
        alias_name: str,
        *,
        etag: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a search alias and its associated mapping to an index.

        :param alias_name: The name of the alias to delete. Required.
        :type alias_name: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    async def delete_alias(
        self,
        alias: _models.SearchAlias,
        /,
        *,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a search alias and its associated mapping to an index.

        :param alias: The SearchAlias object to delete. Required.
        :type alias: ~azure.search.documents.indexes.models.SearchAlias
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def delete_alias(self, *args: Union[str, _models.SearchAlias], **kwargs: Any) -> None:
        """Deletes a search alias and its associated mapping to an index.

        :param alias_name: The name of the alias to delete. Required.
        :type alias_name: str
        :param alias: The SearchAlias object to delete.
        :type alias: ~azure.search.documents.indexes.models.SearchAlias
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if args and isinstance(args[0], _models.SearchAlias):
            alias = args[0]
            kwargs.setdefault("etag", alias.e_tag)
            return await super().delete_alias(alias.name, **kwargs)
        else:
            return await super().delete_alias(*args, **kwargs)

    @overload
    async def delete_agent(
        self,
        agent_name: str,
        *,
        etag: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a knowledge agent.

        :param agent_name: The name of the agent to delete. Required.
        :type agent_name: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    async def delete_agent(
        self,
        agent: _models.KnowledgeAgent,
        /,
        *,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a knowledge agent.

        :param agent: The KnowledgeAgent object to delete. Required.
        :type agent: ~azure.search.documents.indexes.models.KnowledgeAgent
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def delete_agent(self, *args: Union[str, _models.KnowledgeAgent], **kwargs: Any) -> None:
        """Deletes a knowledge agent.

        :param agent_name: The name of the agent to delete. Required.
        :type agent_name: str
        :param agent: The KnowledgeAgent object to delete.
        :type agent: ~azure.search.documents.indexes.models.KnowledgeAgent
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if args and isinstance(args[0], _models.KnowledgeAgent):
            agent = args[0]
            kwargs.setdefault("etag", agent.e_tag)
            return await super().delete_agent(agent.name, **kwargs)
        else:
            return await super().delete_agent(*args, **kwargs)

    @overload
    async def delete_knowledge_source(
        self,
        source_name: str,
        *,
        etag: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a knowledge source.

        :param source_name: The name of the knowledge source to delete. Required.
        :type source_name: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    async def delete_knowledge_source(
        self,
        knowledge_source: _models.KnowledgeSource,
        /,
        *,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a knowledge source.

        :param knowledge_source: The KnowledgeSource object to delete. Required.
        :type knowledge_source: ~azure.search.documents.indexes.models.KnowledgeSource
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def delete_knowledge_source(self, *args: Union[str, _models.KnowledgeSource], **kwargs: Any) -> None:
        """Deletes a knowledge source.

        :param source_name: The name of the knowledge source to delete. Required.
        :type source_name: str
        :param knowledge_source: The KnowledgeSource object to delete.
        :type knowledge_source: ~azure.search.documents.indexes.models.KnowledgeSource
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if args and isinstance(args[0], _models.KnowledgeSource):
            knowledge_source = args[0]
            kwargs.setdefault("etag", knowledge_source.e_tag)
            return await super().delete_knowledge_source(knowledge_source.name, **kwargs)
        else:
            return await super().delete_knowledge_source(*args, **kwargs)

    @distributed_trace
    def list_index_names(self, **kwargs: Any) -> AsyncItemPaged[str]:
        """Lists the names of all indexes available for a search service.

        :return: An async iterator like instance of index names
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        names = self.list_indexes(cls=lambda objs: [x.get("name") for x in objs], **kwargs)
        return cast(AsyncItemPaged[str], names)

    @distributed_trace_async
    async def get_synonym_maps(self, **kwargs: Any) -> List[_models.SynonymMap]:
        """Lists all synonym maps available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a
         comma-separated list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: str
        :return: List of synonym maps
        :rtype: list[~azure.search.documents.indexes.models.SynonymMap]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._get_synonym_maps(**kwargs)
        assert result.synonym_maps is not None  # Hint for mypy
        typed_result = [cast(_models.SynonymMap, x) for x in result.synonym_maps]
        return typed_result

    @distributed_trace_async
    async def get_synonym_map_names(self, **kwargs: Any) -> List[str]:
        """Lists the names of all synonym maps available for a search service.

        :return: List of synonym map names
        :rtype: list[str]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self.get_synonym_maps(**kwargs)
        return [x.get("name") for x in result]

    @distributed_trace
    def list_alias_names(self, **kwargs) -> AsyncItemPaged[str]:
        """List the alias names in an Azure Search service.

        :return: List of alias names
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError: If the operation fails.
        """
        names = self.list_aliases(cls=lambda objs: [x.get("name") for x in objs], **kwargs)
        return cast(AsyncItemPaged[str], names)


class _SearchIndexerClientOperationsMixin(_SearchIndexerClientOperationsMixinGenerated):
    """Custom operations mixin for SearchIndexerClient (async)."""

    @overload
    async def delete_data_source_connection(
        self,
        data_source_name: str,
        *,
        etag: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a data source connection.

        :param data_source_name: The name of the data source connection to delete. Required.
        :type data_source_name: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    async def delete_data_source_connection(
        self,
        data_source: _models.SearchIndexerDataSourceConnection,
        /,
        *,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a data source connection.

        :param data_source: The SearchIndexerDataSourceConnection object to delete. Required.
        :type data_source: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def delete_data_source_connection(
        self, *args: Union[str, _models.SearchIndexerDataSourceConnection], **kwargs: Any
    ) -> None:
        """Deletes a data source connection.

        :param data_source_name: The name of the data source connection to delete. Required.
        :type data_source_name: str
        :param data_source: The SearchIndexerDataSourceConnection object to delete.
        :type data_source: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if args and isinstance(args[0], _models.SearchIndexerDataSourceConnection):
            data_source = args[0]
            kwargs.setdefault("etag", data_source.e_tag)
            return await super().delete_data_source_connection(data_source.name, **kwargs)
        else:
            return await super().delete_data_source_connection(*args, **kwargs)

    @overload
    async def delete_indexer(
        self,
        indexer_name: str,
        *,
        etag: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes an indexer.

        :param indexer_name: The name of the indexer to delete. Required.
        :type indexer_name: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    async def delete_indexer(
        self,
        indexer: _models.SearchIndexer,
        /,
        *,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes an indexer.

        :param indexer: The SearchIndexer object to delete. Required.
        :type indexer: ~azure.search.documents.indexes.models.SearchIndexer
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def delete_indexer(self, *args: Union[str, _models.SearchIndexer], **kwargs: Any) -> None:
        """Deletes an indexer.

        :param indexer_name: The name of the indexer to delete. Required.
        :type indexer_name: str
        :param indexer: The SearchIndexer object to delete.
        :type indexer: ~azure.search.documents.indexes.models.SearchIndexer
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if args and isinstance(args[0], _models.SearchIndexer):
            indexer = args[0]
            kwargs.setdefault("etag", indexer.e_tag)
            return await super().delete_indexer(indexer.name, **kwargs)
        else:
            return await super().delete_indexer(*args, **kwargs)

    @overload
    async def delete_skillset(
        self,
        skillset_name: str,
        *,
        etag: str | None = None,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a skillset.

        :param skillset_name: The name of the skillset to delete. Required.
        :type skillset_name: str
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @overload
    async def delete_skillset(
        self,
        skillset: _models.SearchIndexerSkillset,
        /,
        *,
        match_condition: MatchConditions | None = None,
        **kwargs: Any,
    ) -> None:
        """Deletes a skillset.

        :param skillset: The SearchIndexerSkillset object to delete. Required.
        :type skillset: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def delete_skillset(self, *args: Union[str, _models.SearchIndexerSkillset], **kwargs: Any) -> None:
        """Deletes a skillset.

        :param skillset_name: The name of the skillset to delete. Required.
        :type skillset_name: str
        :param skillset: The SearchIndexerSkillset object to delete.
        :type skillset: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if args and isinstance(args[0], _models.SearchIndexerSkillset):
            skillset = args[0]
            kwargs.setdefault("etag", skillset.e_tag)
            return await super().delete_skillset(skillset.name, **kwargs)
        else:
            return await super().delete_skillset(*args, **kwargs)

    @overload
    async def get_skillsets(self, *, select: str | None = None, **kwargs: Any) -> List[_models.SearchIndexerSkillset]:
        """Lists all skillsets available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a comma-separated
         list of JSON property names, or '*' for all properties. The default is all properties. Default
         value is None.
        :paramtype select: str
        :return: List of all the SearchIndexerSkillsets.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexerSkillset]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def get_skillsets(self, **kwargs: Any) -> List[_models.SearchIndexerSkillset]:
        """Lists all skillsets available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a comma-separated
         list of JSON property names, or '*' for all properties. The default is all properties. Default
         value is None.
        :paramtype select: str
        :return: List of all the SearchIndexerSkillsets.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexerSkillset]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._get_skillsets(**kwargs)
        assert result.skillsets is not None  # Hint for mypy
        typed_result = [cast(_models.SearchIndexerSkillset, x) for x in result.skillsets]
        return typed_result

    @overload
    async def get_indexers(self, *, select: str | None = None, **kwargs: Any) -> List[_models.SearchIndexer]:
        """Lists all indexers available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a comma-separated
         list of JSON property names, or '*' for all properties. The default is all properties. Default
         value is None.
        :paramtype select: str
        :return: List of all the SearchIndexers.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexer]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        ...

    @distributed_trace_async
    async def get_indexers(self, **kwargs: Any) -> List[_models.SearchIndexer]:
        """Lists all indexers available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a comma-separated
         list of JSON property names, or '*' for all properties. The default is all properties. Default
         value is None.
        :paramtype select: str
        :return: List of all the SearchIndexers.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexer]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_indexers_operations_async.py
                :start-after: [START list_indexer_async]
                :end-before: [END list_indexer_async]
                :language: python
                :dedent: 4
                :caption: List all the SearchIndexers
        """
        result = await self._get_indexers(**kwargs)
        assert result.indexers is not None  # Hint for mypy
        typed_result = [cast(_models.SearchIndexer, x) for x in result.indexers]
        return typed_result

    @distributed_trace_async
    async def get_indexer_names(self, **kwargs) -> Sequence[str]:
        """Lists all indexer names available for a search service.

        :return: List of all the SearchIndexer names.
        :rtype: list[str]
        """
        result = await self.get_indexers(**kwargs)
        return [x.get("name") for x in result]

    @overload
    async def get_data_source_connections(
        self, *, select: str | None = None, **kwargs: Any
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
        ...

    @distributed_trace_async
    async def get_data_source_connections(self, **kwargs: Any) -> List[_models.SearchIndexerDataSourceConnection]:
        """Lists all data source connections available for a search service.

        :keyword select: Selects which top-level properties to retrieve. Specified as a comma-separated
         list of JSON property names, or '*' for all properties. The default is all properties. Default
         value is None.
        :paramtype select: str
        :return: List of all the data source connections.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START list_data_source_connection]
                :end-before: [END list_data_source_connection]
                :language: python
                :dedent: 4
                :caption: List all the data source connections
        """
        result = await self._get_data_source_connections(**kwargs)
        assert result.data_sources is not None  # Hint for mypy
        typed_result = [cast(_models.SearchIndexerDataSourceConnection, x) for x in result.data_sources]
        return typed_result

    @distributed_trace_async
    async def get_data_source_connection_names(self, **kwargs) -> Sequence[str]:
        """Lists all data source connection names available for a search service.

        :return: List of all the data source connection names.
        :rtype: list[str]

        """
        result = await self.get_data_source_connections(**kwargs)
        return [x.get("name") for x in result]

    @distributed_trace_async
    async def get_skillset_names(self, **kwargs) -> Sequence[str]:
        """List the SearchIndexerSkillset names in an Azure Search service.

        :return: List of SearchIndexerSkillset names
        :rtype: list[str]
        :raises ~azure.core.exceptions.HttpResponseError: If there is an error in the REST request.

        """
        result = await self.get_skillsets(**kwargs)
        return [x.get("name") for x in result]


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
