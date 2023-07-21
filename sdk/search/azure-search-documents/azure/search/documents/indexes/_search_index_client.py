# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, List, Union, Optional

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged

from .._api_versions import DEFAULT_VERSION
from ._generated import SearchServiceClient as _SearchServiceClient
from ._utils import (
    get_access_conditions,
    normalize_endpoint,
)
from .._headers_mixin import HeadersMixin
from .._utils import get_authentication_policy
from .._version import SDK_MONIKER
from .._search_client import SearchClient
from .models import SearchIndex, SynonymMap, SearchAlias, AnalyzeTextOptions, AnalyzeResult


class SearchIndexClient(HeadersMixin):  # pylint:disable=too-many-public-methods
    """A client to interact with Azure search service index.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authorize search client requests
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :keyword str api_version: The Search API version to use for requests.
    :keyword str audience: sets the Audience to use for authentication with Azure Active Directory (AAD). The
     audience is not considered when using a shared key. If audience is not provided, the public cloud audience
     will be assumed.
    """

    _ODATA_ACCEPT: str = "application/json;odata.metadata=minimal"

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._endpoint = normalize_endpoint(endpoint)
        self._credential = credential
        audience = kwargs.pop("audience", None)
        if isinstance(credential, AzureKeyCredential):
            self._aad = False
            self._client: _SearchServiceClient = _SearchServiceClient(
                endpoint=endpoint, sdk_moniker=SDK_MONIKER, api_version=self._api_version, **kwargs
            )
        else:
            self._aad = True
            authentication_policy = get_authentication_policy(credential, audience=audience)
            self._client: _SearchServiceClient = _SearchServiceClient(
                endpoint=endpoint,
                authentication_policy=authentication_policy,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        return self._client.__exit__(*args)

    def close(self) -> None:
        """Close the :class:`~azure.search.documents.indexes.SearchIndexClient` session."""
        return self._client.close()

    def get_search_client(self, index_name: str, **kwargs: Any) -> SearchClient:
        """Return a client to perform operations on Search

        :param index_name: The name of the Search Index
        :type index_name: str
        :return: SearchClient object
        :rtype: ~azure.search.documents.SearchClient

        """
        return SearchClient(self._endpoint, index_name, self._credential, **kwargs)

    @distributed_trace
    def list_indexes(self, *, select: Optional[List[str]] = None, **kwargs: Any) -> ItemPaged[SearchIndex]:
        """List the indexes in an Azure Search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
         list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: list[str]
        :return: List of indexes
        :rtype: ~azure.core.paging.ItemPaged[~azure.search.documents.indexes.models.SearchIndex]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if select:
            kwargs["select"] = ",".join(select)
        # pylint:disable=protected-access
        return self._client.indexes.list(cls=lambda objs: [SearchIndex._from_generated(x) for x in objs], **kwargs)

    @distributed_trace
    def list_index_names(self, **kwargs: Any) -> ItemPaged[str]:
        """List the index names in an Azure Search service.

        :return: List of index names
        :rtype: ~azure.core.paging.ItemPaged[str]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        return self._client.indexes.list(cls=lambda objs: [x.name for x in objs], **kwargs)

    @distributed_trace
    def get_index(self, name: str, **kwargs: Any) -> SearchIndex:
        """

        :param name: The name of the index to retrieve.
        :type name: str
        :return: SearchIndex object
        :rtype: ~azure.search.documents.indexes.models.SearchIndex
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_index_crud_operations.py
                :start-after: [START get_index]
                :end-before: [END get_index]
                :language: python
                :dedent: 4
                :caption: Get an index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.indexes.get(name, **kwargs)
        return SearchIndex._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace
    def get_index_statistics(self, index_name: str, **kwargs: Any) -> Dict:
        """Returns statistics for the given index, including a document count
        and storage usage.

        :param index_name: The name of the index to retrieve.
        :type index_name: str
        :return: Statistics for the given index, including a document count and storage usage.
        :rtype: Dict
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.indexes.get_statistics(index_name, **kwargs)
        return result.as_dict()

    @distributed_trace
    def delete_index(
        self,
        index: Union[str, SearchIndex],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> None:
        """Deletes a search index and all the documents it contains. The model must be
        provided instead of the name to use the access conditions.

        :param index: The index name or object to delete.
        :type index: str or ~azure.search.documents.indexes.models.SearchIndex
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_index_crud_operations.py
                :start-after: [START delete_index]
                :end-before: [END delete_index]
                :language: python
                :dedent: 4
                :caption: Delete an index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(index, match_condition)
        kwargs.update(access_condition)
        try:
            index_name = index.name
        except AttributeError:
            index_name = index
        self._client.indexes.delete(index_name=index_name, error_map=error_map, **kwargs)

    @distributed_trace
    def create_index(self, index: SearchIndex, **kwargs: Any) -> SearchIndex:
        """Creates a new search index.

        :param index: The index object.
        :type index: ~azure.search.documents.indexes.models.SearchIndex
        :return: The index created
        :rtype: ~azure.search.documents.indexes.models.SearchIndex
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_index_crud_operations.py
                :start-after: [START create_index]
                :end-before: [END create_index]
                :language: python
                :dedent: 4
                :caption: Creating a new index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        patched_index = index._to_generated()  # pylint:disable=protected-access
        result = self._client.indexes.create(patched_index, **kwargs)
        return SearchIndex._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace
    def create_or_update_index(
        self,
        index: SearchIndex,
        allow_index_downtime: Optional[bool] = None,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> SearchIndex:
        """Creates a new search index or updates an index if it already exists.

        :param index: The index object.
        :type index: ~azure.search.documents.indexes.models.SearchIndex
        :param allow_index_downtime: Allows new analyzers, tokenizers, token filters, or char filters
         to be added to an index by taking the index offline for at least a few seconds. This
         temporarily causes indexing and query requests to fail. Performance and write availability of
         the index can be impaired for several minutes after the index is updated, or longer for very
         large indexes.
        :type allow_index_downtime: bool
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The index created or updated
        :rtype: ~azure.search.documents.indexes.models.SearchIndex
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`, \
        :class:`~azure.core.exceptions.ResourceModifiedError`, \
        :class:`~azure.core.exceptions.ResourceNotModifiedError`, \
        :class:`~azure.core.exceptions.ResourceNotFoundError`, \
        :class:`~azure.core.exceptions.ResourceExistsError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_index_crud_operations.py
                :start-after: [START update_index]
                :end-before: [END update_index]
                :language: python
                :dedent: 4
                :caption: Update an index.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(index, match_condition)
        kwargs.update(access_condition)
        patched_index = index._to_generated()  # pylint:disable=protected-access
        result = self._client.indexes.create_or_update(
            index_name=index.name,
            index=patched_index,
            allow_index_downtime=allow_index_downtime,
            prefer="return=representation",
            error_map=error_map,
            **kwargs
        )
        return SearchIndex._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace
    def analyze_text(self, index_name: str, analyze_request: AnalyzeTextOptions, **kwargs: Any) -> AnalyzeResult:
        """Shows how an analyzer breaks text into tokens.

        :param index_name: The name of the index for which to test an analyzer.
        :type index_name: str
        :param analyze_request: The text and analyzer or analysis components to test.
        :type analyze_request: ~azure.search.documents.indexes.models.AnalyzeTextOptions
        :return: AnalyzeResult
        :rtype: ~azure.search.documents.indexes.models.AnalyzeResult
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_analyze_text.py
                :start-after: [START simple_analyze_text]
                :end-before: [END simple_analyze_text]
                :language: python
                :dedent: 4
                :caption: Analyze text
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.indexes.analyze(
            index_name=index_name,
            request=analyze_request._to_analyze_request(),  # pylint:disable=protected-access
            **kwargs
        )
        return result

    @distributed_trace
    def get_synonym_maps(self, *, select: Optional[List[str]] = None, **kwargs) -> List[SynonymMap]:
        """List the Synonym Maps in an Azure Search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
         list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: list[str]
        :return: List of synonym maps
        :rtype: list[~azure.search.documents.indexes.models.SynonymMap]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_synonym_map_operations.py
                :start-after: [START get_synonym_maps]
                :end-before: [END get_synonym_maps]
                :language: python
                :dedent: 4
                :caption: List Synonym Maps

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if select:
            kwargs["select"] = ",".join(select)
        result = self._client.synonym_maps.list(**kwargs)
        # pylint:disable=protected-access
        return [SynonymMap._from_generated(x) for x in result.synonym_maps]

    @distributed_trace
    def get_synonym_map_names(self, **kwargs: Any) -> List[str]:
        """List the Synonym Map names in an Azure Search service.

        :return: List of synonym maps
        :rtype: list[str]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.synonym_maps.list(**kwargs)
        return [x.name for x in result.synonym_maps]

    @distributed_trace
    def get_synonym_map(self, name: str, **kwargs: Any) -> SynonymMap:
        """Retrieve a named Synonym Map in an Azure Search service

        :param name: The name of the Synonym Map to get
        :type name: str
        :return: The retrieved Synonym Map
        :rtype: :class:`~azure.search.documents.indexes.models.SynonymMap`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_synonym_map_operations.py
                :start-after: [START get_synonym_map]
                :end-before: [END get_synonym_map]
                :language: python
                :dedent: 4
                :caption: Get a Synonym Map

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.synonym_maps.get(name, **kwargs)
        return SynonymMap._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace
    def delete_synonym_map(
        self,
        synonym_map: Union[str, SynonymMap],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> None:
        """Delete a named Synonym Map in an Azure Search service. To use access conditions,
        the SynonymMap model must be provided instead of the name. It is enough to provide
        the name of the synonym map to delete unconditionally.

        :param name: The synonym map name or object to delete
        :type name: str or ~azure.search.documents.indexes.models.SynonymMap
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_synonym_map_operations.py
                :start-after: [START delete_synonym_map]
                :end-before: [END delete_synonym_map]
                :language: python
                :dedent: 4
                :caption: Delete a Synonym Map

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(synonym_map, match_condition)
        kwargs.update(access_condition)
        try:
            name = synonym_map.name
        except AttributeError:
            name = synonym_map
        self._client.synonym_maps.delete(synonym_map_name=name, error_map=error_map, **kwargs)

    @distributed_trace
    def create_synonym_map(self, synonym_map: SynonymMap, **kwargs: Any) -> SynonymMap:
        """Create a new Synonym Map in an Azure Search service

        :param synonym_map: The Synonym Map object
        :type synonym_map: ~azure.search.documents.indexes.models.SynonymMap
        :return: The created Synonym Map
        :rtype: ~azure.search.documents.indexes.models.SynonymMap

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_synonym_map_operations.py
                :start-after: [START create_synonym_map]
                :end-before: [END create_synonym_map]
                :language: python
                :dedent: 4
                :caption: Create a Synonym Map

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        patched_synonym_map = synonym_map._to_generated()  # pylint:disable=protected-access
        result = self._client.synonym_maps.create(patched_synonym_map, **kwargs)
        return SynonymMap._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace
    def create_or_update_synonym_map(
        self,
        synonym_map: SynonymMap,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> SynonymMap:
        """Create a new Synonym Map in an Azure Search service, or update an
        existing one.

        :param synonym_map: The Synonym Map object
        :type synonym_map: ~azure.search.documents.indexes.models.SynonymMap
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The created or updated Synonym Map
        :rtype: ~azure.search.documents.indexes.models.SynonymMap

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(synonym_map, match_condition)
        kwargs.update(access_condition)
        patched_synonym_map = synonym_map._to_generated()  # pylint:disable=protected-access
        result = self._client.synonym_maps.create_or_update(
            synonym_map_name=synonym_map.name,
            synonym_map=patched_synonym_map,
            prefer="return=representation",
            error_map=error_map,
            **kwargs
        )
        return SynonymMap._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace
    def get_service_statistics(self, **kwargs: Any) -> Dict:
        """Get service level statistics for a search service.

        :return: Service statistics result.
        :rtype: dict
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.get_service_statistics(**kwargs)
        return result.as_dict()

    @distributed_trace
    def list_aliases(self, *, select: Optional[List[str]] = None, **kwargs: Any) -> ItemPaged[SearchAlias]:
        """List the aliases in an Azure Search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
         list of JSON property names, or '*' for all properties. The default is all
         properties.
        :paramtype select: list[str]
        :return: List of Aliases
        :rtype: ~azure.core.paging.ItemPaged[~azure.search.documents.indexes.models.SearchAlias]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if select:
            kwargs["select"] = ",".join(select)
        # pylint:disable=protected-access
        return self._client.aliases.list(**kwargs)

    @distributed_trace
    def list_alias_names(self, **kwargs: Any) -> ItemPaged[str]:
        """List the alias names in an Azure Search service.

        :return: List of alias names
        :rtype: ~azure.core.paging.ItemPaged[str]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        return self._client.aliases.list(cls=lambda objs: [x.name for x in objs], **kwargs)

    @distributed_trace
    def get_alias(self, name: str, **kwargs: Any) -> SearchAlias:
        """

        :param name: The name of the alias to retrieve.
        :type name: str
        :return: SearchAlias object
        :rtype: ~azure.search.documents.indexes.models.SearchAlias
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.aliases.get(name, **kwargs)
        return result

    @distributed_trace
    def delete_alias(
        self,
        alias: Union[str, SearchAlias],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> None:
        """Deletes a search alias and its associated mapping to an index. This operation is permanent,
        with no recovery option. The mapped index is untouched by this operation

        :param alias: The alias name or object to delete.
        :type alias: str or ~azure.search.documents.indexes.models.SearchAlias
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :raises: ~azure.core.exceptions.HttpResponseError
        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_index_alias_crud_operations.py
                :start-after: [START delete_alias]
                :end-before: [END delete_alias]
                :language: python
                :dedent: 4
                :caption: Deleting an alias.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(alias, match_condition)
        kwargs.update(access_condition)
        try:
            alias_name = alias.name
        except AttributeError:
            alias_name = alias
        self._client.aliases.delete(alias_name=alias_name, error_map=error_map, **kwargs)

    @distributed_trace
    def create_alias(self, alias: SearchAlias, **kwargs: Any) -> SearchAlias:
        """Creates a new search alias.

        :param alias: The alias object.
        :type alias: ~azure.search.documents.indexes.models.SearchAlias
        :return: The alias created
        :rtype: ~azure.search.documents.indexes.models.SearchAlias
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_index_alias_crud_operations.py
                :start-after: [START create_alias]
                :end-before: [END create_alias]
                :language: python
                :dedent: 4
                :caption: Creating a new alias.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.aliases.create(alias, **kwargs)
        return result  # pylint:disable=protected-access

    @distributed_trace
    def create_or_update_alias(
        self, alias: SearchAlias, *, match_condition: MatchConditions = MatchConditions.Unconditionally, **kwargs: Any
    ) -> SearchAlias:
        """Creates a new search alias or updates an alias if it already exists.

        :param alias: The definition of the alias to create or update.
        :type alias: ~azure.search.documents.indexes.models.SearchAlias
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The index created or updated
        :rtype: ~azure.search.documents.indexes.models.SearchAlias
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`, \
        :class:`~azure.core.exceptions.ResourceModifiedError`, \
        :class:`~azure.core.exceptions.ResourceNotModifiedError`, \
        :class:`~azure.core.exceptions.ResourceNotFoundError`, \
        :class:`~azure.core.exceptions.ResourceExistsError`
        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_index_alias_crud_operations.py
                :start-after: [START update_alias]
                :end-before: [END update_alias]
                :language: python
                :dedent: 4
                :caption: Updating an alias.
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(alias, match_condition)
        kwargs.update(access_condition)
        result = self._client.aliases.create_or_update(
            alias_name=alias.name, alias=alias, prefer="return=representation", error_map=error_map, **kwargs
        )
        return result  # pylint:disable=protected-access
