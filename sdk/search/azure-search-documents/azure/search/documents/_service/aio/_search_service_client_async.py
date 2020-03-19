# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.core.tracing.decorator_async import distributed_trace_async
from .._generated.aio import SearchServiceClient as _SearchServiceClient
from ..._credential import HeadersMixin
from ..._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, List, Union
    from ... import SearchApiKeyCredential


class SearchServiceClient(HeadersMixin):
    """A client to interact with an existing Azure search service.

    :param endpoint: The URL endpoint of an Azure search service
    :type endpoint: str
    :param credential: A credential to authorize search client requests
    :type credential: SearchApiKeyCredential

    """

    _ODATA_ACCEPT = "application/json;odata.metadata=minimal"  # type: str

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, SearchApiKeyCredential, **Any) -> None

        self._endpoint = endpoint  # type: str
        self._credential = credential  # type: SearchApiKeyCredential
        self._client = _SearchServiceClient(
            endpoint=endpoint, sdk_moniker=SDK_MONIKER, **kwargs
        )  # type: _SearchServiceClient

    def __repr__(self):
        # type: () -> str
        return "<SearchServiceClient [endpoint={}]>".format(repr(self._endpoint))[:1024]

    @distributed_trace_async
    async def get_service_statistics(self, **kwargs):
        # type: (**Any) -> dict
        """Get service level statistics for a search service.

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.get_service_statistics(**kwargs)
        return result.as_dict()

    ### Index Operations

    @distributed_trace_async
    async def list_indexes(self, **kwargs):
        # type: (**Any) -> List[dict]
        """List the indexes in an Azure Search service.

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexes.list(**kwargs)
        return result.as_dict()["indexes"]

    @distributed_trace_async
    async def get_index(self, index_name, **kwargs):
        # type: (str, **Any) -> dict
        """

        :param index_name: The name of the index to retrieve.
        :type index_name: str

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexes.get(index_name, **kwargs)
        return result.as_dict()

    @distributed_trace_async
    async def get_index_statistics(self, index_name, **kwargs):
        # type: (str, **Any) -> dict
        """Returns statistics for the given index, including a document count
        and storage usage.

        :param index_name: The name of the index to retrieve.
        :type index_name: str

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        result = await self._client.indexes.get_statistics(index_name, **kwargs)
        return result.as_dict()

    @distributed_trace_async
    async def delete_index(self, index_name, **kwargs):
        # type: (str, **Any) -> None
        """Deletes a search index and all the documents it contains.

        :param index_name: The name of the index to retrieve.
        :type index_name: str

        """
        kwargs["headers"] = self._merge_client_headers(kwargs.get("headers"))
        await self._client.indexes.delete(index_name, **kwargs)

    async def close(self):
        # type: () -> None
        """Close the :class:`~azure.search.SearchServiceClient` session.

        """
        return await self._client.close()

    async def __aenter__(self):
        # type: () -> SearchServiceClient
        await self._client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        await self._client.__aexit__(*args)  # pylint:disable=no-member
