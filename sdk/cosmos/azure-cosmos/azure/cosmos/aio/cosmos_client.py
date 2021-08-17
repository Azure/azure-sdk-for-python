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

"""Create, read, and delete databases in the Azure Cosmos DB SQL API service.
"""

from typing import Any, Dict, Optional, Union, cast, Iterable, List  # pylint: disable=unused-import

import six
from azure.core.tracing.decorator import distributed_trace  # type: ignore

from ..cosmos_client import _parse_connection_str, _build_auth
from ._cosmos_client_connection_async import CosmosClientConnection
from .._base import build_options
from ._retry_utility import ConnectionRetryPolicy
# from .database import DatabaseProxy
from ..documents import ConnectionPolicy, DatabaseAccount
from ..exceptions import CosmosResourceNotFoundError

__all__ = ("CosmosClient",)


def _build_connection_policy(kwargs):
    # type: (Dict[str, Any]) -> ConnectionPolicy
    # pylint: disable=protected-access
    policy = kwargs.pop('connection_policy', None) or ConnectionPolicy()

    # Connection config
    policy.RequestTimeout = kwargs.pop('request_timeout', None) or \
        kwargs.pop('connection_timeout', None) or \
        policy.RequestTimeout
    policy.ConnectionMode = kwargs.pop('connection_mode', None) or policy.ConnectionMode
    policy.ProxyConfiguration = kwargs.pop('proxy_config', None) or policy.ProxyConfiguration
    policy.EnableEndpointDiscovery = kwargs.pop('enable_endpoint_discovery', None) or policy.EnableEndpointDiscovery
    policy.PreferredLocations = kwargs.pop('preferred_locations', None) or policy.PreferredLocations
    policy.UseMultipleWriteLocations = kwargs.pop('multiple_write_locations', None) or \
        policy.UseMultipleWriteLocations

    # SSL config
    verify = kwargs.pop('connection_verify', None)
    policy.DisableSSLVerification = not bool(verify if verify is not None else True)
    ssl = kwargs.pop('ssl_config', None) or policy.SSLConfiguration
    if ssl:
        ssl.SSLCertFile = kwargs.pop('connection_cert', None) or ssl.SSLCertFile
        ssl.SSLCaCerts = verify or ssl.SSLCaCerts
        policy.SSLConfiguration = ssl

    # Retry config
    retry = kwargs.pop('retry_options', None) or policy.RetryOptions
    total_retries = kwargs.pop('retry_total', None)
    retry._max_retry_attempt_count = total_retries or retry._max_retry_attempt_count
    retry._fixed_retry_interval_in_milliseconds = kwargs.pop('retry_fixed_interval', None) or \
        retry._fixed_retry_interval_in_milliseconds
    max_backoff = kwargs.pop('retry_backoff_max', None)
    retry._max_wait_time_in_seconds = max_backoff or retry._max_wait_time_in_seconds
    policy.RetryOptions = retry
    connection_retry = kwargs.pop('connection_retry_policy', None) or policy.ConnectionRetryConfiguration
    if not connection_retry:
        connection_retry = ConnectionRetryPolicy(
            retry_total=total_retries,
            retry_connect=kwargs.pop('retry_connect', None),
            retry_read=kwargs.pop('retry_read', None),
            retry_status=kwargs.pop('retry_status', None),
            retry_backoff_max=max_backoff,
            retry_on_status_codes=kwargs.pop('retry_on_status_codes', []),
            retry_backoff_factor=kwargs.pop('retry_backoff_factor', 0.8),
        )
    policy.ConnectionRetryConfiguration = connection_retry

    return policy



class CosmosClient(object):
    """A client-side logical representation of an Azure Cosmos DB account.

    Use this client to configure and execute requests to the Azure Cosmos DB service.

    :param str url: The URL of the Cosmos DB account.
    :param credential: Can be the account key, or a dictionary of resource tokens.
    :type credential: str or dict[str, str]
    :param str consistency_level: Consistency level to use for the session. The default value is "Session".

    .. admonition:: Example:

        .. literalinclude:: ../samples/examples.py
            :start-after: [START create_client]
            :end-before: [END create_client]
            :language: python
            :dedent: 0
            :caption: Create a new instance of the Cosmos DB client:
            :name: create_client
    """

    def __init__(self, url, credential, **kwargs):
        # type: (str, Any, str, Any) -> None
        """Instantiate a new CosmosClient."""
        auth = _build_auth(credential)
        consistency_level = kwargs.get('consistency_level', 'Session')
        connection_policy = _build_connection_policy(kwargs)
        self.client_connection = CosmosClientConnection(
            url,
            auth=auth,
            consistency_level=consistency_level,
            connection_policy=connection_policy,
            **kwargs
        )

    def __repr__(self):
        # type () -> str
        return "<CosmosClient [{}]>".format(self.client_connection.url_connection)[:1024]

    async def __aenter__(self):
        await self.client_connection.pipeline_client.__enter__()
        await self.client_connection._setup()
        return self

    async def __aexit__(self, *args):
        return await self.client_connection.pipeline_client.__exit__(*args)

    async def close(self):
        await self.__aexit__()

    @classmethod
    def from_connection_string(cls, conn_str, credential=None, consistency_level="Session", **kwargs):
        # type: (str, Optional[Any], str, Any) -> CosmosClient
        """Create a CosmosClient instance from a connection string.

        This can be retrieved from the Azure portal.For full list of optional
        keyword arguments, see the CosmosClient constructor.

        :param str conn_str: The connection string.
        :param credential: Alternative credentials to use instead of the key
            provided in the connection string.
        :type credential: str or dict(str, str)
        :param str consistency_level:
            Consistency level to use for the session. The default value is "Session".
        """
        settings = _parse_connection_str(conn_str, credential)
        return cls(
            url=settings['AccountEndpoint'],
            credential=credential or settings['AccountKey'],
            consistency_level=consistency_level,
            **kwargs
        )
