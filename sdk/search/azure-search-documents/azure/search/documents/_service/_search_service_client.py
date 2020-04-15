# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.tracing.decorator import distributed_trace
from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceNotModifiedError,
)
from ._generated import SearchServiceClient as _SearchServiceClient
from ._generated.models import AccessCondition, Skillset, SynonymMap
from .._headers_mixin import HeadersMixin
from .._version import SDK_MONIKER
from ._utils import (
    delistize_flags_for_index,
    listize_flags_for_index,
    listize_synonyms,
    prep_if_match,
    prep_if_none_match,
    skillset_as_dict,
)

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, List, Sequence, Union
    from azure.core.credentials import AzureKeyCredential
    from ._generated.models import Skill
    from .. import Index, AnalyzeResult, AnalyzeRequest


class SearchServiceClient(HeadersMixin):
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
        """Close the :class:`~azure.search.SearchServiceClient` session.

        """
        return self._client.close()

    ### Service Operations

    @distributed_trace
    def get_service_statistics(self, **kwargs):
        # type: (**Any) -> dict
        """Get service level statistics for a search service.

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.get_service_statistics(**kwargs)
        return result.as_dict()

    ### Index Operations

    @distributed_trace
    def list_indexes(self, **kwargs):
        # type: (**Any) -> List[Index]
        """List the indexes in an Azure Search service.

        :return: List of indexes
        :rtype: list[~azure.search.documents.Index]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.indexes.list(**kwargs)
        indexes = [listize_flags_for_index(x) for x in result.indexes]
        return indexes

    @distributed_trace
    def get_index(self, index_name, **kwargs):
        # type: (str, **Any) -> Index
        """

        :param index_name: The name of the index to retrieve.
        :type index_name: str
        :return: Index object
        :rtype: ~azure.search.documents.Index
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
        result = self._client.indexes.get(index_name, **kwargs)
        return listize_flags_for_index(result)

    @distributed_trace
    def get_index_statistics(self, index_name, **kwargs):
        # type: (str, **Any) -> dict
        """Returns statistics for the given index, including a document count
        and storage usage.

        :param index_name: The name of the index to retrieve.
        :type index_name: str
        :return: Statistics for the given index, including a document count and storage usage.
        :rtype: ~azure.search.documents.GetIndexStatisticsResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.indexes.get_statistics(index_name, **kwargs)
        return result.as_dict()

    @distributed_trace
    def delete_index(self, index_name, **kwargs):
        # type: (str, **Any) -> None
        """Deletes a search index and all the documents it contains.

        :param index_name: The name of the index to retrieve.
        :type index_name: str
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
        self._client.indexes.delete(index_name, **kwargs)

    @distributed_trace
    def create_index(self, index, **kwargs):
        # type: (Index, **Any) -> Index
        """Creates a new search index.

        :param index: The index object.
        :type index: ~azure.search.documents.Index
        :return: The index created
        :rtype: ~azure.search.documents.Index
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
        patched_index = delistize_flags_for_index(index)
        result = self._client.indexes.create(patched_index, **kwargs)
        return result

    @distributed_trace
    def create_or_update_index(
        self,
        index_name,
        index,
        allow_index_downtime=None,
        match_condition=MatchConditions.Unconditionally,
        **kwargs
    ):
        # type: (str, Index, bool, MatchConditions, **Any) -> Index
        """Creates a new search index or updates an index if it already exists.

        :param index_name: The name of the index.
        :type index_name: str
        :param index: The index object.
        :type index: ~azure.search.documents.Index
        :param allow_index_downtime: Allows new analyzers, tokenizers, token filters, or char filters
         to be added to an index by taking the index offline for at least a few seconds. This
         temporarily causes indexing and query requests to fail. Performance and write availability of
         the index can be impaired for several minutes after the index is updated, or longer for very
         large indexes.
        :type allow_index_downtime: bool
        :param match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :return: The index created or updated
        :rtype: :class:`~azure.search.documents.Index`
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
        error_map = {404: ResourceNotFoundError}
        access_condition = None
        if index.e_tag:
            access_condition = AccessCondition()
            access_condition.if_match = prep_if_match(index.e_tag, match_condition)
            access_condition.if_none_match = prep_if_none_match(
                index.e_tag, match_condition
            )
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        if match_condition == MatchConditions.IfModified:
            error_map[304] = ResourceNotModifiedError
        if match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        if match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        patched_index = delistize_flags_for_index(index)
        result = self._client.indexes.create_or_update(
            index_name=index_name,
            index=patched_index,
            allow_index_downtime=allow_index_downtime,
            access_condition=access_condition,
            **kwargs
        )
        return result

    @distributed_trace
    def analyze_text(self, index_name, analyze_request, **kwargs):
        # type: (str, AnalyzeRequest, **Any) -> AnalyzeResult
        """Shows how an analyzer breaks text into tokens.

        :param index_name: The name of the index for which to test an analyzer.
        :type index_name: str
        :param analyze_request: The text and analyzer or analysis components to test.
        :type analyze_request: ~azure.search.documents.AnalyzeRequest
        :return: AnalyzeResult
        :rtype: ~azure.search.documents.AnalyzeResult
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
            index_name=index_name, request=analyze_request, **kwargs
        )
        return result

    # Synonym Maps Operations

    @distributed_trace
    def list_synonym_maps(self, **kwargs):
        # type: (**Any) -> List[Index]
        """List the Synonym Maps in an Azure Search service.

        :return: List of synonym maps
        :rtype: list[dict]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_synonym_map_operations.py
                :start-after: [START list_synonym_map]
                :end-before: [END list_synonym_map]
                :language: python
                :dedent: 4
                :caption: List Synonym Maps

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.synonym_maps.list(**kwargs)
        return [listize_synonyms(x) for x in result.as_dict()["synonym_maps"]]

    @distributed_trace
    def get_synonym_map(self, name, **kwargs):
        # type: (str, **Any) -> dict
        """Retrieve a named Synonym Map in an Azure Search service

        :param name: The name of the Synonym Map to get
        :type name: str
        :return: The retrieved Synonym Map
        :rtype: dict
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
        return listize_synonyms(result.as_dict())

    @distributed_trace
    def delete_synonym_map(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Delete a named Synonym Map in an Azure Search service

        :param name: The name of the Synonym Map to delete
        :type name: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_synonym_map_operations.py
                :start-after: [START delete_synonym_map]
                :end-before: [END delete_synonym_map]
                :language: python
                :dedent: 4
                :caption: Delete a Synonym Map

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        self._client.synonym_maps.delete(name, **kwargs)

    @distributed_trace
    def create_synonym_map(self, name, synonyms, **kwargs):
        # type: (str, Sequence[str], **Any) -> dict
        """Create a new Synonym Map in an Azure Search service

        :param name: The name of the Synonym Map to create
        :type name: str
        :param synonyms: The list of synonyms in SOLR format
        :type synonyms: List[str]
        :return: The created Synonym Map
        :rtype: dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_synonym_map_operations.py
                :start-after: [START create_synonym_map]
                :end-before: [END create_synonym_map]
                :language: python
                :dedent: 4
                :caption: Create a Synonym Map

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        solr_format_synonyms = "\n".join(synonyms)
        synonym_map = SynonymMap(name=name, synonyms=solr_format_synonyms)
        result = self._client.synonym_maps.create(synonym_map, **kwargs)
        return listize_synonyms(result.as_dict())

    @distributed_trace
    def create_or_update_synonym_map(self, name, synonyms, **kwargs):
        # type: (str, Sequence[str], **Any) -> dict
        """Create a new Synonym Map in an Azure Search service, or update an
        existing one.

        :param name: The name of the Synonym Map to create or update
        :type name: str
        :param synonyms: A list of synonyms in SOLR format
        :type synonyms: List[str]
        :return: The created or updated Synonym Map
        :rtype: dict

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        solr_format_synonyms = "\n".join(synonyms)
        synonym_map = SynonymMap(name=name, synonyms=solr_format_synonyms)
        result = self._client.synonym_maps.create_or_update(name, synonym_map, **kwargs)
        return listize_synonyms(result.as_dict())

    # Skillset Operations

    @distributed_trace
    def list_skillsets(self, **kwargs):
        # type: (**Any) -> List[dict]
        """List the Skillsets in an Azure Search service.

        :return: List of Skillsets
        :rtype: list[dict]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START list_skillsets]
                :end-before: [END list_skillsets]
                :language: python
                :dedent: 4
                :caption: List Skillsets

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.skillsets.list(**kwargs)
        return [skillset_as_dict(x) for x in result.skillsets]

    @distributed_trace
    def get_skillset(self, name, **kwargs):
        # type: (str, **Any) -> dict
        """Retrieve a named Skillset in an Azure Search service

        :param name: The name of the Skillset to get
        :type name: str
        :return: The retrieved Skillset
        :rtype: dict
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START get_skillset]
                :end-before: [END get_skillset]
                :language: python
                :dedent: 4
                :caption: Get a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.skillsets.get(name, **kwargs)
        return skillset_as_dict(result)

    @distributed_trace
    def delete_skillset(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Delete a named Skillset in an Azure Search service

        :param name: The name of the Skillset to delete
        :type name: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START delete_skillset]
                :end-before: [END delete_skillset]
                :language: python
                :dedent: 4
                :caption: Delete a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        self._client.skillsets.delete(name, **kwargs)

    @distributed_trace
    def create_skillset(self, name, skills, description, **kwargs):
        # type: (str, Sequence[Skill], str, **Any) -> dict
        """Create a new Skillset in an Azure Search service

        :param name: The name of the Skillset to create
        :type name: str
        :param skills: A list of Skill objects to include in the Skillset
        :type skills: List[Skill]]
        :param description: A description for the Skillset
        :type description: Optional[str]
        :return: The created Skillset
        :rtype: dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START create_skillset]
                :end-before: [END create_skillset]
                :language: python
                :dedent: 4
                :caption: Create a Skillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        skillset = Skillset(name=name, skills=list(skills), description=description)

        result = self._client.skillsets.create(skillset, **kwargs)
        return skillset_as_dict(result)

    @distributed_trace
    def create_or_update_skillset(self, name, skills, description, **kwargs):
        # type: (str, Sequence[Skill], str, **Any) -> dict
        """Create a new Skillset in an Azure Search service, or update an
        existing one.

        :param name: The name of the Skillset to create or update
        :type name: str
        :param skills: A list of Skill objects to include in the Skillset
        :type skills: List[Skill]
        :param description: A description for the Skillset
        :type description: Optional[str]
        :return: The created or updated Skillset
        :rtype: dict

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        skillset = Skillset(name=name, skills=list(skills), description=description)

        result = self._client.skillsets.create_or_update(name, skillset, **kwargs)
        return skillset_as_dict(result)
