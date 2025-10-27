# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Iterator, cast, List, Sequence

from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._operations import (
    _SearchIndexClientOperationsMixin as _SearchIndexClientOperationsMixinGenerated,
    _SearchIndexerClientOperationsMixin as _SearchIndexerClientOperationsMixinGenerated,
)

class _SearchIndexClientOperationsMixin(_SearchIndexClientOperationsMixinGenerated):
    """Custom operations mixin for SearchIndexClient."""

    @distributed_trace
    def list_index_names(self, **kwargs: Any) -> ItemPaged[str]:
        """Lists the names of all indexes available for a search service.

        :return: An iterator like instance of index names
        :rtype: ~azure.core.paging.ItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        names = self.list_indexes(cls=lambda objs: [x.name for x in objs], **kwargs)
        return cast(ItemPaged[str], names)

    @distributed_trace
    def get_synonym_map_names(self, **kwargs: Any) -> List[str]:
        """Lists the names of all synonym maps available for a search service.

        :return: List of synonym maps
        :rtype: list[str]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self.get_synonym_maps(**kwargs)
        assert result.synonym_maps is not None  # Hint for mypy
        return [x.name for x in result.synonym_maps]

    @distributed_trace
    def list_alias_names(self, **kwargs: Any) -> ItemPaged[str]:
        """List the alias names in an Azure Search service.

        :return: List of alias names
        :rtype: ~azure.core.paging.ItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError: If the operation fails.

        """
        names = self.list_aliases(cls=lambda objs: [x.name for x in objs], **kwargs)
        return cast(ItemPaged[str], names)


class _SearchIndexerClientOperationsMixin(_SearchIndexerClientOperationsMixinGenerated):
    """Custom operations mixin for SearchIndexerClient."""
    @distributed_trace
    def get_indexer_names(self, **kwargs: Any) -> Sequence[str]:
        """Lists all indexer names available for a search service.

        :return: List of all the SearchIndexers.
        :rtype: list[str]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexers_operations.py
                :start-after: [START list_indexer]
                :end-before: [END list_indexer]
                :language: python
                :dedent: 4
                :caption: List all the SearchIndexers
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self.list_indexers(**kwargs)
        assert result.indexers is not None  # Hint for mypy
        return [x.name for x in result.indexers]
    
    @distributed_trace
    def get_data_source_connection_names(self, **kwargs: Any) -> Sequence[str]:
        """Lists all data source connection names available for a search service.

        :return: List of all the data source connection names.
        :rtype: list[str]

        """
        result = self.list_data_sources(**kwargs)
        assert result.data_sources is not None  # Hint for mypy
        return [x.name for x in result.data_sources]
    
    @distributed_trace
    def get_skillset_names(self, **kwargs: Any) -> List[str]:
        """List the SearchIndexerSkillset names in an Azure Search service.

        :return: List of SearchIndexerSkillset names
        :rtype: list[str]
        :raises ~azure.core.exceptions.HttpResponseError: If there is an error in the REST request.

        """
        result = self.list_skillsets(**kwargs)
        assert result.skillsets is not None  # Hint for mypy
        return [x.name for x in result.skillsets]

__all__: list[str] = ["_SearchIndexClientOperationsMixin", "_SearchIndexerClientOperationsMixin"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
