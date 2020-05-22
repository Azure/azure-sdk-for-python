# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core import MatchConditions
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError

from ._generated import SearchServiceClient as _SearchServiceClient
from ._generated.models import SearchIndexerSkillset
from ._utils import get_access_conditions, normalize_endpoint
from ..._headers_mixin import HeadersMixin
from ..._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from ._generated.models import SearchIndexer, SearchIndexerStatus
    from typing import Any, Dict, Optional, Sequence
    from azure.core.credentials import AzureKeyCredential


class SearchIndexerClient(HeadersMixin):
    """A client to interact with Azure search service Indexers.

    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, **Any) -> None

        self._endpoint = normalize_endpoint(endpoint)  # type: str
        self._credential = credential  # type: AzureKeyCredential
        self._client = _SearchServiceClient(
            endpoint=endpoint, sdk_moniker=SDK_MONIKER, **kwargs
        )  # type: _SearchServiceClient

    def __enter__(self):
        # type: () -> SearchIndexerClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        return self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.SearchIndexerClient` session.

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

    @distributed_trace
    def create_datasource(self, data_source, **kwargs):
        # type: (SearchIndexerDataSource, **Any) -> Dict[str, Any]
        """Creates a new datasource.

        :param data_source: The definition of the datasource to create.
        :type data_source: ~search.models.SearchIndexerDataSource
        :return: The created SearchIndexerDataSource
        :rtype: dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START create_data_source]
                :end-before: [END create_data_source]
                :language: python
                :dedent: 4
                :caption: Create a Data Source
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.data_sources.create(data_source, **kwargs)
        return result

    @distributed_trace
    def create_or_update_datasource(self, data_source, name=None, **kwargs):
        # type: (SearchIndexerDataSource, Optional[str], **Any) -> Dict[str, Any]
        """Creates a new datasource or updates a datasource if it already exists.
        :param name: The name of the datasource to create or update.
        :type name: str
        :param data_source: The definition of the datasource to create or update.
        :type data_source: ~search.models.SearchIndexerDataSource
        :keyword match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :return: The created SearchIndexerDataSource
        :rtype: dict
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            data_source, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        if not name:
            name = data_source.name
        result = self._client.data_sources.create_or_update(
            data_source_name=name,
            data_source=data_source,
            error_map=error_map,
            **kwargs
        )
        return result

    @distributed_trace
    def get_datasource(self, name, **kwargs):
        # type: (str, **Any) -> Dict[str, Any]
        """Retrieves a datasource definition.

        :param name: The name of the datasource to retrieve.
        :type name: str
        :return: The SearchIndexerDataSource that is fetched.
        :rtype: dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START get_data_source]
                :end-before: [END get_data_source]
                :language: python
                :dedent: 4
                :caption: Retrieve a SearchIndexerDataSource
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.data_sources.get(name, **kwargs)
        return result

    @distributed_trace
    def get_datasources(self, **kwargs):
        # type: (**Any) -> Sequence[SearchIndexerDataSource]
        """Lists all datasources available for a search service.

        :return: List of all the data sources.
        :rtype: `list[dict]`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START list_data_source]
                :end-before: [END list_data_source]
                :language: python
                :dedent: 4
                :caption: List all the SearchIndexerDataSources
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.data_sources.list(**kwargs)
        return result.data_sources

    @distributed_trace
    def delete_datasource(self, data_source, **kwargs):
        # type: (Union[str, SearchIndexerDataSource], **Any) -> None
        """Deletes a datasource. To use access conditions, the Datasource model must be
        provided instead of the name. It is enough to provide the name of the datasource
        to delete unconditionally

        :param data_source: The datasource to delete.
        :type data_source: str or ~search.models.SearchIndexerDataSource
        :keyword match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START delete_data_source]
                :end-before: [END delete_data_source]
                :language: python
                :dedent: 4
                :caption: Delete a SearchIndexerDataSource
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            data_source, kwargs.pop("match_condition", MatchConditions.Unconditionally)
        )
        kwargs.update(access_condition)
        try:
            name = data_source.name
        except AttributeError:
            name = data_source
        self._client.data_sources.delete(
            data_source_name=name, error_map=error_map, **kwargs
        )

    @distributed_trace
    def get_skillsets(self, **kwargs):
        # type: (**Any) -> List[SearchIndexerSkillset]
        """List the SearchIndexerSkillsets in an Azure Search service.

        :return: List of SearchIndexerSkillsets
        :rtype: list[dict]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START get_skillsets]
                :end-before: [END get_skillsets]
                :language: python
                :dedent: 4
                :caption: List SearchIndexerSkillsets

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.skillsets.list(**kwargs)
        return result.skillsets

    @distributed_trace
    def get_skillset(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndexerSkillset
        """Retrieve a named SearchIndexerSkillset in an Azure Search service

        :param name: The name of the SearchIndexerSkillset to get
        :type name: str
        :return: The retrieved SearchIndexerSkillset
        :rtype: dict
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START get_skillset]
                :end-before: [END get_skillset]
                :language: python
                :dedent: 4
                :caption: Get a SearchIndexerSkillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return self._client.skillsets.get(name, **kwargs)

    @distributed_trace
    def delete_skillset(self, skillset, **kwargs):
        # type: (Union[str, SearchIndexerSkillset], **Any) -> None
        """Delete a named SearchIndexerSkillset in an Azure Search service. To use access conditions,
        the SearchIndexerSkillset model must be provided instead of the name. It is enough to provide
        the name of the skillset to delete unconditionally

        :param name: The SearchIndexerSkillset to delete
        :type name: str or ~search.models.SearchIndexerSkillset
        :keyword match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
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
        self._client.skillsets.delete(name, error_map=error_map, **kwargs)

    @distributed_trace
    def create_skillset(self, name, skills, description, **kwargs):
        # type: (str, Sequence[SearchIndexerSkill], str, **Any) -> SearchIndexerSkillset
        """Create a new SearchIndexerSkillset in an Azure Search service

        :param name: The name of the SearchIndexerSkillset to create
        :type name: str
        :param skills: A list of Skill objects to include in the SearchIndexerSkillset
        :type skills: List[SearchIndexerSkill]]
        :param description: A description for the SearchIndexerSkillset
        :type description: Optional[str]
        :return: The created SearchIndexerSkillset
        :rtype: dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_skillset_operations.py
                :start-after: [START create_skillset]
                :end-before: [END create_skillset]
                :language: python
                :dedent: 4
                :caption: Create a SearchIndexerSkillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        skillset = SearchIndexerSkillset(
            name=name, skills=list(skills), description=description
        )

        return self._client.skillsets.create(skillset, **kwargs)

    @distributed_trace
    def create_or_update_skillset(self, name, **kwargs):
        # type: (str, **Any) -> SearchIndexerSkillset
        """Create a new SearchIndexerSkillset in an Azure Search service, or update an
        existing one. The skillset param must be provided to perform the
        operation with access conditions.

        :param name: The name of the SearchIndexerSkillset to create or update
        :type name: str
        :keyword skills: A list of Skill objects to include in the SearchIndexerSkillset
        :type skills: List[SearchIndexerSkill]
        :keyword description: A description for the SearchIndexerSkillset
        :type description: Optional[str]
        :keyword skillset: A SearchIndexerSkillset to create or update.
        :type skillset: :class:`~azure.search.documents.SearchIndexerSkillset`
        :keyword match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :return: The created or updated SearchIndexerSkillset
        :rtype: dict

        If a `skillset` is passed in, any optional `skills`, or
        `description` parameter values will override it.

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError}
        access_condition = None

        if "skillset" in kwargs:
            skillset = kwargs.pop("skillset")
            error_map, access_condition = get_access_conditions(
                skillset, kwargs.pop("match_condition", MatchConditions.Unconditionally)
            )
            kwargs.update(access_condition)
            skillset = SearchIndexerSkillset.deserialize(skillset.serialize())
            skillset.name = name
            for param in ("description", "skills"):
                if param in kwargs:
                    setattr(skillset, param, kwargs.pop(param))
        else:

            skillset = SearchIndexerSkillset(
                name=name,
                description=kwargs.pop("description", None),
                skills=kwargs.pop("skills", None),
            )

        return self._client.skillsets.create_or_update(
            skillset_name=name, skillset=skillset, error_map=error_map, **kwargs
        )
