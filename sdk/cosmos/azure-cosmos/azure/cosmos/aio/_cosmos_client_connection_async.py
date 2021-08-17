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

# disable (too-many-lines) check
# pylint: disable=C0302

"""Document client class for the Azure Cosmos database service.
"""
# https://github.com/PyCQA/pylint/issues/3112
# Currently pylint is locked to 2.3.3 and this is fixed in 2.4.4
from typing import Dict, Any, Optional # pylint: disable=unused-import
import six
import asyncio
from urllib3.util.retry import Retry
from azure.core.async_paging import AsyncItemPaged
from azure.core import AsyncPipelineClient
from azure.core import PipelineClient
from azure.core.exceptions import raise_with_traceback  # type: ignore
from azure.core.pipeline.policies import (
    AsyncHTTPPolicy,
    ContentDecodePolicy,
    HeadersPolicy,
    UserAgentPolicy,
    NetworkTraceLoggingPolicy,
    CustomHookPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    ProxyPolicy)

from .. import _base as base
from .. import documents
from ..documents import ConnectionPolicy
from .. import _constants as constants
from .. import http_constants
from .. import _query_iterable as query_iterable
from .. import _runtime_constants as runtime_constants
from .. import _request_object
from .. import _synchronized_request as synchronized_request
from . import _asynchronous_request as asynchronous_request
from .. import _global_endpoint_manager as global_endpoint_manager
from . import _global_endpoint_manager_async as global_endpoint_manager_async
from .._routing import routing_map_provider
from ._retry_utility import ConnectionRetryPolicy
from .. import _session
from .. import _utils
from ..partition_key import _Undefined, _Empty

# pylint: disable=protected-access


class CosmosClientConnection(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """Represents a document client.

    Provides a client-side logical representation of the Azure Cosmos
    service. This client is used to configure and execute requests against the
    service.

    The service client encapsulates the endpoint and credentials used to access
    the Azure Cosmos service.
    """

    class _QueryCompatibilityMode:
        Default = 0
        Query = 1
        SqlQuery = 2

    # default number precisions
    _DefaultNumberHashPrecision = 3
    _DefaultNumberRangePrecision = -1

    # default string precision
    _DefaultStringHashPrecision = 3
    _DefaultStringRangePrecision = -1

    def __init__(
        self,
        url_connection,  # type: str
        auth,  # type: Dict[str, Any]
        connection_policy=None,  # type: Optional[ConnectionPolicy]
        consistency_level=documents.ConsistencyLevel.Session,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """
        :param str url_connection:
            The URL for connecting to the DB server.
        :param dict auth:
            Contains 'masterKey' or 'resourceTokens', where
            auth['masterKey'] is the default authorization key to use to
            create the client, and auth['resourceTokens'] is the alternative
            authorization key.
        :param documents.ConnectionPolicy connection_policy:
            The connection policy for the client.
        :param documents.ConsistencyLevel consistency_level:
            The default consistency policy for client operations.

        """
        self.url_connection = url_connection

        self.master_key = None
        self.resource_tokens = None
        if auth is not None:
            self.master_key = auth.get("masterKey")
            self.resource_tokens = auth.get("resourceTokens")

            if auth.get("permissionFeed"):
                self.resource_tokens = {}
                for permission_feed in auth["permissionFeed"]:
                    resource_parts = permission_feed["resource"].split("/")
                    id_ = resource_parts[-1]
                    self.resource_tokens[id_] = permission_feed["_token"]

        self.connection_policy = connection_policy or ConnectionPolicy()

        self.partition_resolvers = {}  # type: Dict[str, Any]

        self.partition_key_definition_cache = {}  # type: Dict[str, Any]

        self.default_headers = {
            http_constants.HttpHeaders.CacheControl: "no-cache",
            http_constants.HttpHeaders.Version: http_constants.Versions.CurrentVersion,
            # For single partition query with aggregate functions we would try to accumulate the results on the SDK.
            # We need to set continuation as not expected.
            http_constants.HttpHeaders.IsContinuationExpected: False,
        }

        if consistency_level is not None:
            self.default_headers[http_constants.HttpHeaders.ConsistencyLevel] = consistency_level

        # Keeps the latest response headers from server.
        self.last_response_headers = None

        if consistency_level == documents.ConsistencyLevel.Session:
            # create a session - this is maintained only if the default consistency level
            # on the client is set to session, or if the user explicitly sets it as a property
            # via setter
            self.session = _session.Session(self.url_connection)
        else:
            self.session = None  # type: ignore

        self._useMultipleWriteLocations = False
        self._global_endpoint_manager = global_endpoint_manager._GlobalEndpointManager(self)

        retry_policy = None
        if isinstance(self.connection_policy.ConnectionRetryConfiguration, AsyncHTTPPolicy):
            retry_policy = self.connection_policy.ConnectionRetryConfiguration
        elif isinstance(self.connection_policy.ConnectionRetryConfiguration, int):
            retry_policy = ConnectionRetryPolicy(total=self.connection_policy.ConnectionRetryConfiguration)
        elif isinstance(self.connection_policy.ConnectionRetryConfiguration, Retry):
            # Convert a urllib3 retry policy to a Pipeline policy
            retry_policy = ConnectionRetryPolicy(
                retry_total=self.connection_policy.ConnectionRetryConfiguration.total,
                retry_connect=self.connection_policy.ConnectionRetryConfiguration.connect,
                retry_read=self.connection_policy.ConnectionRetryConfiguration.read,
                retry_status=self.connection_policy.ConnectionRetryConfiguration.status,
                retry_backoff_max=self.connection_policy.ConnectionRetryConfiguration.BACKOFF_MAX,
                retry_on_status_codes=list(self.connection_policy.ConnectionRetryConfiguration.status_forcelist),
                retry_backoff_factor=self.connection_policy.ConnectionRetryConfiguration.backoff_factor
            )
        else:
            TypeError("Unsupported retry policy. Must be an azure.cosmos.ConnectionRetryPolicy, int, or urllib3.Retry")

        proxies = kwargs.pop('proxies', {})
        if self.connection_policy.ProxyConfiguration and self.connection_policy.ProxyConfiguration.Host:
            host = self.connection_policy.ProxyConfiguration.Host
            url = six.moves.urllib.parse.urlparse(host)
            proxy = host if url.port else host + ":" + str(self.connection_policy.ProxyConfiguration.Port)
            proxies.update({url.scheme : proxy})

        policies = [
            HeadersPolicy(**kwargs),
            ProxyPolicy(proxies=proxies),
            UserAgentPolicy(base_user_agent=_utils.get_user_agent(), **kwargs),
            ContentDecodePolicy(),
            retry_policy,
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
            ]

        transport = kwargs.pop("transport", None)
        self.pipeline_client = AsyncPipelineClient(base_url=url_connection, transport=transport, policies=policies)
        self._setup_kwargs = kwargs

        # Query compatibility mode.
        # Allows to specify compatibility mode used by client when making query requests. Should be removed when
        # application/sql is no longer supported.
        self._query_compatibility_mode = CosmosClientConnection._QueryCompatibilityMode.Default

        # Routing map provider
        self._routing_map_provider = routing_map_provider.SmartRoutingMapProvider(self)

    async def _setup(self):
        if not 'database_account' in self._setup_kwargs:
            self._setup_kwargs['database_account'] = await self._global_endpoint_manager._GetDatabaseAccount(**self._setup_kwargs)
            await self._global_endpoint_manager.force_refresh(self._setup_kwargs['database_account'])
