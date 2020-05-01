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
    from ._generated.models import DataSource
    from typing import Any, Dict, Optional, Sequence, Union
    from azure.core.credentials import AzureKeyCredential


class SearchDataSourcesClient(HeadersMixin):
    """A client to interact with Azure search service Data Sources.

    This class is not normally instantiated directly, instead use
    `get_datasources_client()` from a `SearchServiceClient`

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
        # type: () -> SearchDataSourcesClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        return self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.SearchDataSourcesClient` session.

        """
        return self._client.close()

    @distributed_trace
    def create_datasource(self, data_source, **kwargs):
        # type: (DataSource, **Any) -> Dict[str, Any]
        """Creates a new datasource.

        :param data_source: The definition of the datasource to create.
        :type data_source: ~search.models.DataSource
        :return: The created DataSource
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
        # type: (DataSource, Optional[str], **Any) -> Dict[str, Any]
        """Creates a new datasource or updates a datasource if it already exists.
        :param name: The name of the datasource to create or update.
        :type name: str
        :param data_source: The definition of the datasource to create or update.
        :type data_source: ~search.models.DataSource
        :keyword match_condition: The match condition to use upon the etag
        :type match_condition: ~azure.core.MatchConditions
        :return: The created DataSource
        :rtype: dict
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            data_source,
            kwargs.pop('match_condition', MatchConditions.Unconditionally)
        )
        if not name:
            name = data_source.name
        result = self._client.data_sources.create_or_update(
            data_source_name=name,
            data_source=data_source,
            access_condition=access_condition,
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
        :return: The DataSource that is fetched.
        :rtype: dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START get_data_source]
                :end-before: [END get_data_source]
                :language: python
                :dedent: 4
                :caption: Retrieve a DataSource
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.data_sources.get(name, **kwargs)
        return result

    @distributed_trace
    def get_datasources(self, **kwargs):
        # type: (**Any) -> Sequence[DataSource]
        """Lists all datasources available for a search service.

        :return: List of all the data sources.
        :rtype: `list[dict]`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_source_operations.py
                :start-after: [START list_data_source]
                :end-before: [END list_data_source]
                :language: python
                :dedent: 4
                :caption: List all the DataSources
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = self._client.data_sources.list(**kwargs)
        return result.data_sources

    @distributed_trace
    def delete_datasource(self, data_source, **kwargs):
        # type: (Union[str, DataSource], **Any) -> None
        """Deletes a datasource. To use access conditions, the Datasource model must be
        provided instead of the name. It is enough to provide the name of the datasource
        to delete unconditionally

        :param data_source: The datasource to delete.
        :type data_source: str or ~search.models.DataSource
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
                :caption: Delete a DataSource
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        error_map, access_condition = get_access_conditions(
            data_source,
            kwargs.pop('match_condition', MatchConditions.Unconditionally)
        )
        try:
            name = data_source.name
        except AttributeError:
            name = data_source
        self._client.data_sources.delete(
            data_source_name=name,
            access_condition=access_condition,
            error_map=error_map,
            **kwargs
        )
