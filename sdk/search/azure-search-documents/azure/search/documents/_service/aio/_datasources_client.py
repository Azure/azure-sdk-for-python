# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated.aio import SearchServiceClient as _SearchServiceClient
from ..._headers_mixin import HeadersMixin
from ..._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from .._generated.models import DataSource
    from typing import Any, Dict, Optional, Sequence
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

    async def __aenter__(self):
        # type: () -> SearchDataSourcesClient
        await self._client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        return await self._client.__aexit__(*args)  # pylint:disable=no-member

    async def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.documents.aio.SearchDataSourcesClient` session.

        """
        return await self._client.close()

    @distributed_trace_async
    async def create_datasource(self, data_source, **kwargs):
        # type: (DataSource, **Any) -> Dict[str, Any]
        """Creates a new datasource.
        :param data_source: The definition of the datasource to create.
        :type data_source: ~search.models.DataSource
        :return: The created DataSource
        :rtype: dict

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START create_data_source_async]
                :end-before: [END create_data_source_async]
                :language: python
                :dedent: 4
                :caption: Create a DataSource
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.data_sources.create(data_source, **kwargs)
        return result

    @distributed_trace_async
    async def create_or_update_datasource(self, data_source, name=None, **kwargs):
        # type: (DataSource, Optional[str], **Any) -> Dict[str, Any]
        """Creates a new datasource or updates a datasource if it already exists.

        :param name: The name of the datasource to create or update.
        :type name: str
        :param data_source: The definition of the datasource to create or update.
        :type data_source: ~search.models.DataSource
        :return: The created DataSource
        :rtype: dict
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))

        if not name:
            name = data_source.name
        result = await self._client.data_sources.create_or_update(
            name, data_source, **kwargs
        )
        return result

    @distributed_trace_async
    async def delete_datasource(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Deletes a datasource.

        :param name: The name of the datasource to delete.
        :type name: str

        :return: None
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START delete_data_source_async]
                :end-before: [END delete_data_source_async]
                :language: python
                :dedent: 4
                :caption: Delete a DataSource
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.data_sources.delete(name, **kwargs)
        return result

    @distributed_trace_async
    async def get_datasource(self, name, **kwargs):
        # type: (str, **Any) -> Dict[str, Any]
        """Retrieves a datasource definition.

        :param name: The name of the datasource to retrieve.
        :type name: str
        :return: The DataSource that is fetched.

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START get_data_source_async]
                :end-before: [END get_data_source_async]
                :language: python
                :dedent: 4
                :caption: Retrieve a DataSource
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.data_sources.get(name, **kwargs)
        return result

    @distributed_trace_async
    async def get_datasources(self, **kwargs):
        # type: (**Any) -> Sequence[DataSource]
        """Lists all datasources available for a search service.

        :return: List of all the data sources.
        :rtype: `list[dict]`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_source_operations_async.py
                :start-after: [START list_data_source_async]
                :end-before: [END list_data_source_async]
                :language: python
                :dedent: 4
                :caption: List all DataSources
        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.data_sources.list(**kwargs)
        return result.data_sources
