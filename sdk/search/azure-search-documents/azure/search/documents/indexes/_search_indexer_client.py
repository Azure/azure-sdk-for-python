# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Optional, Sequence, Union, List, cast

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.tracing.decorator import distributed_trace

from ._generated import SearchServiceClient as _SearchServiceClient
from ._generated.models import (
    SearchIndexer,
    SearchIndexerStatus,
)
from ._utils import (
    get_access_conditions,
    normalize_endpoint,
)
from .models import (
    SearchIndexerSkillset,
    EntityRecognitionSkillVersion,
    SearchIndexerDataSourceConnection,
    SentimentSkillVersion,
)
from .._api_versions import DEFAULT_VERSION
from .._headers_mixin import HeadersMixin
from .._utils import get_authentication_policy
from .._version import SDK_MONIKER


class SearchIndexerClient(HeadersMixin):  # pylint: disable=R0904
    """A client to interact with Azure search service Indexers.

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
    _client: _SearchServiceClient

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._endpoint = normalize_endpoint(endpoint)
        self._credential = credential
        audience = kwargs.pop("audience", None)
        if isinstance(credential, AzureKeyCredential):
            self._aad = False
            self._client = _SearchServiceClient(
                endpoint=endpoint, sdk_moniker=SDK_MONIKER, api_version=self._api_version, **kwargs
            )
        else:
            self._aad = True
            authentication_policy = get_authentication_policy(credential, audience=audience)
            self._client = _SearchServiceClient(
                endpoint=endpoint,
                authentication_policy=authentication_policy,
                sdk_moniker=SDK_MONIKER,
                api_version=self._api_version,
                **kwargs
            )

    def __enter__(self) -> "SearchIndexerClient":
        self._client.__enter__()
        return self

    def __exit__(self, *args) -> None:
        return self._client.__exit__(*args)

    def close(self) -> None:
        """Close the session.
        :return: None
        :rtype: None
        """
        return self._client.close()

    @distributed_trace
    def create_indexer(self, indexer: SearchIndexer, **kwargs: Any) -> SearchIndexer:
        """Creates a new SearchIndexer.

        :param indexer: The definition of the indexer to create.
        :type indexer: ~azure.search.documents.indexes.models.SearchIndexer
        :return: The created SearchIndexer
        :rtype: ~azure.search.documents.indexes.models.SearchIndexer

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexers_operations.py
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
    def create_or_update_indexer(
        self,
        indexer: SearchIndexer,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> SearchIndexer:
        """Creates a new indexer or updates an indexer if it already exists.

        :param indexer: The definition of the indexer to create or update.
        :type indexer: ~azure.search.documents.indexes.models.SearchIndexer
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The created SearchIndexer
        :rtype: ~azure.search.documents.indexes.models.SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(indexer, match_condition)
        kwargs.update(access_condition)
        name = indexer.name
        result = self._client.indexers.create_or_update(
            indexer_name=name, indexer=indexer, prefer="return=representation", error_map=error_map, **kwargs
        )
        return result

    @distributed_trace
    def get_indexer(self, name: str, **kwargs: Any) -> SearchIndexer:
        """Retrieves an indexer definition.

        :param name: The name of the indexer to retrieve.
        :type name: str
        :return: The SearchIndexer that is fetched.
        :rtype: ~azure.search.documents.indexes.models.SearchIndexer

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexers_operations.py
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
    def get_indexers(self, *, select: Optional[List[str]] = None, **kwargs: Any) -> Sequence[SearchIndexer]:
        """Lists all indexers available for a search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
            list of JSON property names, or '*' for all properties. The default is all
            properties.
        :paramtype select: list[str]
        :return: List of all the SearchIndexers.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexer]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexers_operations.py
                :start-after: [START list_indexer]
                :end-before: [END list_indexer]
                :language: python
                :dedent: 4
                :caption: List all the SearchIndexers
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if select:
            kwargs["select"] = ",".join(select)
        result = self._client.indexers.list(**kwargs)
        assert result.indexers is not None  # Hint for mypy
        return result.indexers

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
        result = self._client.indexers.list(**kwargs)
        assert result.indexers is not None  # Hint for mypy
        return [x.name for x in result.indexers]

    @distributed_trace
    def delete_indexer(
        self,
        indexer: Union[str, SearchIndexer],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> None:
        """Deletes an indexer. To use access conditions, the SearchIndexer model
        must be provided instead of the name. It is enough to provide
        the name of the indexer to delete unconditionally.

        :param indexer: The indexer to delete.
        :type indexer: str or ~azure.search.documents.indexes.models.SearchIndexer
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexers_operations.py
                :start-after: [START delete_indexer]
                :end-before: [END delete_indexer]
                :language: python
                :dedent: 4
                :caption: Delete a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(indexer, match_condition)
        kwargs.update(access_condition)
        try:
            name = indexer.name  # type: ignore
        except AttributeError:
            name = indexer
        self._client.indexers.delete(name, error_map=error_map, **kwargs)

    @distributed_trace
    def run_indexer(self, name: str, **kwargs: Any) -> None:
        """Run an indexer.

        :param name: The name of the indexer to run.
        :type name: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexers_operations.py
                :start-after: [START run_indexer]
                :end-before: [END run_indexer]
                :language: python
                :dedent: 4
                :caption: Run a SearchIndexer
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        self._client.indexers.run(name, **kwargs)

    @distributed_trace
    def reset_indexer(self, name: str, **kwargs: Any) -> None:
        """Resets the change tracking state associated with an indexer.

        :param name: The name of the indexer to reset.
        :type name: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexers_operations.py
                :start-after: [START reset_indexer]
                :end-before: [END reset_indexer]
                :language: python
                :dedent: 4
                :caption: Reset a SearchIndexer's change tracking state
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        self._client.indexers.reset(name, **kwargs)

    @distributed_trace
    def get_indexer_status(self, name: str, **kwargs: Any) -> SearchIndexerStatus:
        """Get the status of the indexer.

        :param name: The name of the indexer to fetch the status.
        :type name: str

        :return: SearchIndexerStatus
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerStatus

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_indexers_operations.py
                :start-after: [START get_indexer_status]
                :end-before: [END get_indexer_status]
                :language: python
                :dedent: 4
                :caption: Get a SearchIndexer's status
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        return self._client.indexers.get_status(name, **kwargs)

    @distributed_trace
    def create_data_source_connection(
        self, data_source_connection: SearchIndexerDataSourceConnection, **kwargs: Any
    ) -> SearchIndexerDataSourceConnection:
        """Creates a new data source connection.

        :param data_source_connection: The definition of the data source connection to create.
        :type data_source_connection: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :return: The created SearchIndexerDataSourceConnection
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START create_data_source_connection]
                :end-before: [END create_data_source_connection]
                :language: python
                :dedent: 4
                :caption: Create a Data Source
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        # pylint:disable=protected-access
        packed_data_source = data_source_connection._to_generated()
        result = self._client.data_sources.create(packed_data_source, **kwargs)
        return cast(SearchIndexerDataSourceConnection, SearchIndexerDataSourceConnection._from_generated(result))

    @distributed_trace
    def create_or_update_data_source_connection(
        self,
        data_source_connection: SearchIndexerDataSourceConnection,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> SearchIndexerDataSourceConnection:
        """Creates a new data source connection or updates a data source connection if it already exists.
        :param data_source_connection: The definition of the data source connection to create or update.
        :type data_source_connection: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The created SearchIndexerDataSourceConnection
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        """

        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(data_source_connection, match_condition)
        kwargs.update(access_condition)
        name = data_source_connection.name
        packed_data_source = data_source_connection._to_generated()  # pylint:disable=protected-access
        result = self._client.data_sources.create_or_update(
            data_source_name=name,
            data_source=packed_data_source,
            prefer="return=representation",
            error_map=error_map,
            **kwargs
        )
        # pylint:disable=protected-access
        return cast(SearchIndexerDataSourceConnection, SearchIndexerDataSourceConnection._from_generated(result))

    @distributed_trace
    def get_data_source_connection(self, name: str, **kwargs: Any) -> SearchIndexerDataSourceConnection:
        """Retrieves a data source connection definition.

        :param name: The name of the data source connection to retrieve.
        :type name: str
        :return: The SearchIndexerDataSourceConnection that is fetched.
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START get_data_source_connection]
                :end-before: [END get_data_source_connection]
                :language: python
                :dedent: 4
                :caption: Retrieve a SearchIndexerDataSourceConnection
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.data_sources.get(name, **kwargs)
        # pylint:disable=protected-access
        return cast(SearchIndexerDataSourceConnection, SearchIndexerDataSourceConnection._from_generated(result))

    @distributed_trace
    def get_data_source_connections(
        self, *, select: Optional[List[str]] = None, **kwargs: Any
    ) -> Sequence[SearchIndexerDataSourceConnection]:
        """Lists all data source connections available for a search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
            list of JSON property names, or '*' for all properties. The default is all
            properties.
        :paramtype select: list[str]
        :return: List of all the data source connections.
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START list_data_source_connection]
                :end-before: [END list_data_source_connection]
                :language: python
                :dedent: 4
                :caption: List all the SearchIndexerDataSourceConnections
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if select:
            kwargs["select"] = ",".join(select)
        result = self._client.data_sources.list(**kwargs)
        assert result.data_sources is not None  # Hint for mypy
        # pylint:disable=protected-access
        return [SearchIndexerDataSourceConnection._from_generated(x) for x in result.data_sources]

    @distributed_trace
    def get_data_source_connection_names(self, **kwargs: Any) -> Sequence[str]:
        """Lists all data source connection names available for a search service.

        :return: List of all the data source connection names.
        :rtype: list[str]

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.data_sources.list(**kwargs)
        assert result.data_sources is not None  # Hint for mypy
        return [x.name for x in result.data_sources]

    @distributed_trace
    def delete_data_source_connection(
        self,
        data_source_connection: Union[str, SearchIndexerDataSourceConnection],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> None:
        """Deletes a data source connection. To use access conditions, the SearchIndexerDataSourceConnection
        model must be provided instead of the name. It is enough to provide the name of the data source connection
        to delete unconditionally

        :param data_source_connection: The data source connection to delete.
        :type data_source_connection: str or ~azure.search.documents.indexes.models.SearchIndexerDataSourceConnection
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START delete_data_source_connection]
                :end-before: [END delete_data_source_connection]
                :language: python
                :dedent: 4
                :caption: Delete a SearchIndexerDataSourceConnection
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(data_source_connection, match_condition)
        kwargs.update(access_condition)
        try:
            name = data_source_connection.name  # type: ignore
        except AttributeError:
            name = data_source_connection
        self._client.data_sources.delete(data_source_name=name, error_map=error_map, **kwargs)

    @distributed_trace
    def get_skillsets(self, *, select: Optional[List[str]] = None, **kwargs: Any) -> List[SearchIndexerSkillset]:
        # pylint:disable=protected-access
        """List the SearchIndexerSkillsets in an Azure Search service.

        :keyword select: Selects which top-level properties of the skillsets to retrieve. Specified as a
            list of JSON property names, or '*' for all properties. The default is all
            properties.
        :paramtype select: list[str]
        :return: List of SearchIndexerSkillsets
        :rtype: list[~azure.search.documents.indexes.models.SearchIndexerSkillset]

        :raises: ~azure.core.exceptions.HttpResponseError
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        if select:
            kwargs["select"] = ",".join(select)
        result = self._client.skillsets.list(**kwargs)
        assert result.skillsets is not None  # Hint for mypy
        return [SearchIndexerSkillset._from_generated(skillset) for skillset in result.skillsets]

    @distributed_trace
    def get_skillset_names(self, **kwargs: Any) -> List[str]:
        """List the SearchIndexerSkillset names in an Azure Search service.

        :return: List of SearchIndexerSkillset names
        :rtype: list[str]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.skillsets.list(**kwargs)
        assert result.skillsets is not None  # Hint for mypy
        return [x.name for x in result.skillsets]

    @distributed_trace
    def get_skillset(self, name: str, **kwargs: Any) -> SearchIndexerSkillset:
        """Retrieve a named SearchIndexerSkillset in an Azure Search service

        :param name: The name of the SearchIndexerSkillset to get
        :type name: str
        :return: The retrieved SearchIndexerSkillset
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :raises: ~azure.core.exceptions.ResourceNotFoundError
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.skillsets.get(name, **kwargs)
        # pylint:disable=protected-access
        return cast(SearchIndexerSkillset, SearchIndexerSkillset._from_generated(result))

    @distributed_trace
    def delete_skillset(
        self,
        skillset: Union[str, SearchIndexerSkillset],
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> None:
        """Delete a named SearchIndexerSkillset in an Azure Search service. To use access conditions,
        the SearchIndexerSkillset model must be provided instead of the name. It is enough to provide
        the name of the skillset to delete unconditionally

        :param skillset: The SearchIndexerSkillset to delete
        :type skillset: str or ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(skillset, match_condition)
        kwargs.update(access_condition)
        try:
            name = skillset.name  # type: ignore
        except AttributeError:
            name = skillset
        self._client.skillsets.delete(name, error_map=error_map, **kwargs)

    @distributed_trace
    def create_skillset(self, skillset: SearchIndexerSkillset, **kwargs: Any) -> SearchIndexerSkillset:
        # pylint:disable=protected-access
        """Create a new SearchIndexerSkillset in an Azure Search service

        :param skillset: The SearchIndexerSkillset object to create
        :type skillset: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :return: The created SearchIndexerSkillset
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        _validate_skillset(skillset)
        skillset_gen = skillset._to_generated() if hasattr(skillset, "_to_generated") else skillset

        result = self._client.skillsets.create(skillset_gen, **kwargs)
        return cast(SearchIndexerSkillset, SearchIndexerSkillset._from_generated(result))

    @distributed_trace
    def create_or_update_skillset(
        self,
        skillset: SearchIndexerSkillset,
        *,
        match_condition: MatchConditions = MatchConditions.Unconditionally,
        **kwargs: Any
    ) -> SearchIndexerSkillset:
        # pylint:disable=protected-access
        """Create a new SearchIndexerSkillset in an Azure Search service, or update an
        existing one.

        :param skillset: The SearchIndexerSkillset object to create or update
        :type skillset: ~azure.search.documents.indexes.models.SearchIndexerSkillset
        :keyword match_condition: The match condition to use upon the etag
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: The created or updated SearchIndexerSkillset
        :rtype: ~azure.search.documents.indexes.models.SearchIndexerSkillset

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(skillset, match_condition)
        kwargs.update(access_condition)
        _validate_skillset(skillset)
        skillset_gen = skillset._to_generated() if hasattr(skillset, "_to_generated") else skillset

        result = self._client.skillsets.create_or_update(
            skillset_name=skillset.name,
            skillset=skillset_gen,
            prefer="return=representation",
            error_map=error_map,
            **kwargs
        )
        return cast(SearchIndexerSkillset, SearchIndexerSkillset._from_generated(result))


def _validate_skillset(skillset: SearchIndexerSkillset):
    """Validates any multi-version skills in the skillset to verify that unsupported
       parameters are not supplied by the user.

    :param skillset: The skillset to validate
    :type skillset: ~azure.search.documents.indexes.models.SearchIndexerSkillset
    """
    skills = getattr(skillset, "skills", None)
    if not skills:
        return

    error_strings = []
    for skill in skills:
        try:
            skill_version = skill.get("skill_version")
        except AttributeError:
            skill_version = getattr(skill, "skill_version", None)
        if not skill_version:
            continue
        if skill_version == SentimentSkillVersion.V3:
            unsupported = []
        elif skill_version == EntityRecognitionSkillVersion.V3:
            unsupported = ["include_typeless_entities"]

        errors = []
        for item in unsupported:
            try:
                if skill.get(item, None):
                    errors.append(item)
            except AttributeError:
                if skill.__dict__.get(item, None):
                    errors.append(item)
        if errors:
            error_strings.append(
                "Unsupported parameters for skill version {}: {}".format(skill_version, ", ".join(errors))
            )
    if error_strings:
        raise ValueError("\n".join(error_strings))
