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
from . import _asynchronous_request as asynchronous_request
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
        self._global_endpoint_manager = global_endpoint_manager_async._GlobalEndpointManager(self)

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

    async def GetDatabaseAccount(self, url_connection=None, **kwargs):
        """Gets database account info.

        :return:
            The Database Account.
        :rtype:
            documents.DatabaseAccount

        """
        if url_connection is None:
            url_connection = self.url_connection

        initial_headers = dict(self.default_headers)
        headers = base.GetHeaders(self, initial_headers, "get", "", "", "", {})  # path  # id  # type

        request_params = _request_object.RequestObject("databaseaccount", documents._OperationType.Read, url_connection)
        result, self.last_response_headers = await self.__Get("", request_params, headers, **kwargs)
        database_account = documents.DatabaseAccount()
        database_account.DatabasesLink = "/dbs/"
        database_account.MediaLink = "/media/"
        if http_constants.HttpHeaders.MaxMediaStorageUsageInMB in self.last_response_headers:
            database_account.MaxMediaStorageUsageInMB = self.last_response_headers[
                http_constants.HttpHeaders.MaxMediaStorageUsageInMB
            ]
        if http_constants.HttpHeaders.CurrentMediaStorageUsageInMB in self.last_response_headers:
            database_account.CurrentMediaStorageUsageInMB = self.last_response_headers[
                http_constants.HttpHeaders.CurrentMediaStorageUsageInMB
            ]
        database_account.ConsistencyPolicy = result.get(constants._Constants.UserConsistencyPolicy)

        # WritableLocations and ReadableLocations fields will be available only for geo-replicated database accounts
        if constants._Constants.WritableLocations in result:
            database_account._WritableLocations = result[constants._Constants.WritableLocations]
        if constants._Constants.ReadableLocations in result:
            database_account._ReadableLocations = result[constants._Constants.ReadableLocations]
        if constants._Constants.EnableMultipleWritableLocations in result:
            database_account._EnableMultipleWritableLocations = result[
                constants._Constants.EnableMultipleWritableLocations
            ]

        self._useMultipleWriteLocations = (
            self.connection_policy.UseMultipleWriteLocations and database_account._EnableMultipleWritableLocations
        )
        return database_account

    async def ReadDatabase(self, database_link, options=None, **kwargs):
        """Reads a database.

        :param str database_link:
            The link to the database.
        :param dict options:
            The request options for the request.
        :return:
            The Database that was read.
        :rtype: dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(database_link)
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return await self.Read(path, "dbs", database_id, None, options, **kwargs)

    async def ReadContainer(self, collection_link, options=None, **kwargs):
        """Reads a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.

        :return:
            The read Collection.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return await self.Read(path, "colls", collection_id, None, options, **kwargs)

    async def Read(self, path, typ, id, initial_headers, options=None, **kwargs):  # pylint: disable=redefined-builtin
        """Reads a Azure Cosmos resource and returns it.

        :param str path:
        :param str typ:
        :param str id:
        :param dict initial_headers:
        :param dict options:
            The request options for the request.

        :return:
            The upserted Azure Cosmos resource.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self, initial_headers, "get", path, id, typ, options)
        # Read will use ReadEndpoint since it uses GET operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Read)
        result, self.last_response_headers = await self.__Get(path, request_params, headers, **kwargs)
        return result

    async def __Get(self, path, request_params, req_headers, **kwargs):
        """Azure Cosmos 'GET' async http request.

        :params str url:
        :params str path:
        :params dict req_headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        request = self.pipeline_client.get(url=path, headers=req_headers)
        return await asynchronous_request.AsynchronousRequest(
            client=self,
            request_params=request_params,
            global_endpoint_manager=self._global_endpoint_manager,
            connection_policy=self.connection_policy,
            pipeline_client=self.pipeline_client,
            request=request,
            request_data=None,
            **kwargs
        )