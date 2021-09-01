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

"""Interact with databases in the Azure Cosmos DB SQL API service.
"""

from typing import Any, List, Dict, Union, cast, Iterable, Optional

import warnings
import six
from azure.core.tracing.decorator_async import distributed_trace_async  # type: ignore

from ._cosmos_client_connection_async import CosmosClientConnection
from .._base import build_options
from .container import ContainerProxy
from ..offer import Offer
from ..http_constants import StatusCodes
from ..exceptions import CosmosResourceNotFoundError
from ..user import UserProxy
from ..documents import IndexingMode

__all__ = ("DatabaseProxy",)

# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs

class DatabaseProxy(object):
    """An interface to interact with a specific database.

    This class should not be instantiated directly. Instead use the
    :func:`CosmosClient.get_database_client` method.

    A database contains one or more containers, each of which can contain items,
    stored procedures, triggers, and user-defined functions.

    A database can also have associated users, each of which is configured with
    a set of permissions for accessing certain containers, stored procedures,
    triggers, user-defined functions, or items.

    :ivar id: The ID (name) of the database.

    An Azure Cosmos DB SQL API database has the following system-generated
    properties. These properties are read-only:

    * `_rid`:   The resource ID.
    * `_ts`:    When the resource was last updated. The value is a timestamp.
    * `_self`:	The unique addressable URI for the resource.
    * `_etag`:	The resource etag required for optimistic concurrency control.
    * `_colls`:	The addressable path of the collections resource.
    * `_users`:	The addressable path of the users resource.
    """

    def __init__(self, client_connection, id, properties=None):  # pylint: disable=redefined-builtin
        # type: (CosmosClientConnection, str, Dict[str, Any]) -> None
        """
        :param ClientSession client_connection: Client from which this database was retrieved.
        :param str id: ID (name) of the database.
        """
        self.client_connection = client_connection
        self.id = id
        self.database_link = u"dbs/{}".format(self.id)
        self._properties = properties

    def __repr__(self):
        # type () -> str
        return "<DatabaseProxy [{}]>".format(self.database_link)[:1024]

    @distributed_trace_async
    async def read(self, populate_query_metrics=None, **kwargs):
        # type: (Optional[bool], Any) -> Dict[str, Any]
        """Read the database properties.

        :param bool populate_query_metrics: Enable returning query metrics in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :rtype: Dict[Str, Any]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given database couldn't be retrieved.
        """
        # TODO this helper function should be extracted from CosmosClient
        from .cosmos_client import CosmosClient

        database_link = CosmosClient._get_database_link(self)
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        self._properties = await self.client_connection.ReadDatabase(
            database_link, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, self._properties)

        return cast('Dict[str, Any]', self._properties)

    def get_container_client(self, container):
        # type: (Union[str, ContainerProxy, Dict[str, Any]]) -> ContainerProxy
        """Get a `ContainerProxy` for a container with specified ID (name).

        :param container: The ID (name) of the container, a :class:`ContainerProxy` instance,
            or a dict representing the properties of the container to be retrieved.
        :rtype: ~azure.cosmos.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START get_container]
                :end-before: [END get_container]
                :language: python
                :dedent: 0
                :caption: Get an existing container, handling a failure if encountered:
                :name: get_container
        """
        if isinstance(container, ContainerProxy):
            id_value = container.id
        else:
            try:
                id_value = container["id"]
            except TypeError:
                id_value = container

        return ContainerProxy(self.client_connection, self.database_link, id_value)