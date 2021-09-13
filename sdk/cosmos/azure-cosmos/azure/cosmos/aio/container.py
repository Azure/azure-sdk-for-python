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

    async def _get_properties(self):
        # type: () -> Dict[str, Any]
        if self._properties is None:
            self._properties = await self.read()
        return self._properties

    @property
    async def is_system_key(self):
        # type: () -> bool
        if self._is_system_key is None:
            properties = await self._get_properties()
            self._is_system_key = (
                properties["partitionKey"]["systemKey"] if "systemKey" in properties["partitionKey"] else False
            )
        return cast('bool', self._is_system_key)

    def _get_document_link(self, item_or_link):
        # type: (Union[Dict[str, Any], str]) -> str
        if isinstance(item_or_link, six.string_types):
            return u"{}/docs/{}".format(self.container_link, item_or_link)
        return item_or_link["_self"]

    def _set_partition_key(self, partition_key):
        if partition_key == NonePartitionKeyValue:
            return CosmosClientConnection._return_undefined_or_empty_partition_key(self.is_system_key) #might have to await here
        return partition_key

    @distributed_trace_async
    async def create_item(
        self,
        body,  # type: Dict[str, Any]
        populate_query_metrics=None,  # type: Optional[bool]
        pre_trigger_include=None,  # type: Optional[str]
        post_trigger_include=None,  # type: Optional[str]
        indexing_directive=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, str]
        """Create an item in the container.

        To update or replace an existing item, use the
        :func:`ContainerProxy.upsert_item` method.

        :param body: A dict-like object representing the item to create.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param pre_trigger_include: trigger id to be used as pre operation trigger.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :param indexing_directive: Indicate whether the document should be omitted from indexing.
        :keyword bool enable_automatic_id_generation: Enable automatic id generation if no id present.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the new item.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Item with the given ID already exists.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        request_options["disableAutomaticIdGeneration"] = not kwargs.pop('enable_automatic_id_generation', False)
        if populate_query_metrics:
            request_options["populateQueryMetrics"] = populate_query_metrics
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include
        if indexing_directive is not None:
            request_options["indexingDirective"] = indexing_directive

        result = await self.client_connection.CreateItem(
            database_or_container_link=self.container_link, document=body, options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

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

    @distributed_trace_async
    async def read_item(
        self,
        item,  # type: Union[str, Dict[str, Any]]
        partition_key,  # type: Any
        populate_query_metrics=None,  # type: Optional[bool]
        post_trigger_include=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, str]
        """Get the item identified by `item`.

        :param item: The ID (name) or dict representing item to retrieve.
        :param partition_key: Partition key for the item to retrieve.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: Dict representing the item to be retrieved.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item couldn't be retrieved.
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START update_item]
                :end-before: [END update_item]
                :language: python
                :dedent: 0
                :caption: Get an item from the database and update one of its properties:
                :name: update_item
        """
        doc_link = self._get_document_link(item)
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        
        if partition_key is not None:
            request_options["partitionKey"] = self._set_partition_key(partition_key)
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include

        result = await self.client_connection.ReadItem(document_link=doc_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace_async
    async def delete_item(
        self,
        item,  # type: Union[Dict[str, Any], str]
        partition_key,  # type: Any
        populate_query_metrics=None,  # type: Optional[bool]
        pre_trigger_include=None,  # type: Optional[str]
        post_trigger_include=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete the specified item from the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be deleted.
        :param partition_key: Specifies the partition key value for the item.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param pre_trigger_include: trigger id to be used as pre operation trigger.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The item wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The item does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if partition_key is not None:
            request_options["partitionKey"] = self._set_partition_key(partition_key)
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include

        document_link = self._get_document_link(item)
        result = await self.client_connection.DeleteItem(document_link=document_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
