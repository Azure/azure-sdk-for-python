# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Create, read, update and delete items in the Azure Cosmos DB SQL API service.
"""

from typing import Any, Dict, List, Optional, Union, Iterable, cast  # pylint: disable=unused-import

import six
import asyncio
import time
from azure.core.tracing.decorator_async import distributed_trace_async  # type: ignore

from ._cosmos_client_connection_async import CosmosClientConnection
from .._base import build_options
from ..exceptions import CosmosResourceNotFoundError
from ..http_constants import StatusCodes
from ..offer import Offer
from ..scripts import ScriptsProxy
from ..partition_key import NonePartitionKeyValue

__all__ = ("ContainerProxy",)

# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs


class ContainerProxy(object):
    """An interface to interact with a specific DB Container.

    This class should not be instantiated directly. Instead, use the
    :func:`DatabaseProxy.get_container_client` method to get an existing
    container, or the :func:`Database.create_container` method to create a
    new container.

    A container in an Azure Cosmos DB SQL API database is a collection of
    documents, each of which is represented as an Item.

    :ivar str id: ID (name) of the container
    :ivar str session_token: The session token for the container.
    """

    def __init__(self, client_connection, database_link, id, properties=None):  # pylint: disable=redefined-builtin
        # type: (CosmosClientConnection, str, str, Dict[str, Any]) -> None
        self.client_connection = client_connection
        self.id = id
        self._properties = properties
        self.container_link = u"{}/colls/{}".format(database_link, self.id)
        self._is_system_key = None
        self._scripts = None  # type: Optional[ScriptsProxy]

    def __repr__(self):
        # type () -> str
        return "<ContainerProxy [{}]>".format(self.container_link)[:1024]

    @distributed_trace_async
    async def read(
        self,
        populate_query_metrics=None,  # type: Optional[bool]
        populate_partition_key_range_statistics=None,  # type: Optional[bool]
        populate_quota_info=None,  # type: Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Read the container properties.

        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param populate_partition_key_range_statistics: Enable returning partition key
            range statistics in response headers.
        :param populate_quota_info: Enable returning collection storage quota information in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be retrieved.
            This includes if the container does not exist.
        :returns: Dict representing the retrieved container.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics
        if populate_partition_key_range_statistics is not None:
            request_options["populatePartitionKeyRangeStatistics"] = populate_partition_key_range_statistics
        if populate_quota_info is not None:
            request_options["populateQuotaInfo"] = populate_quota_info

        collection_link = self.container_link
        self._properties = await self.client_connection.ReadContainer(
            collection_link, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, self._properties)

        return cast('Dict[str, Any]', self._properties)