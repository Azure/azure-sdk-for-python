# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, Union, List, TYPE_CHECKING

from ._common import EventData

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential, AzureSasCredential, AzureNamedKeyCredential


class EventHubBufferedProducerClient(object):
    """The EventHubBufferedProducerClient

    :ivar fully_qualified_namespace:
    :vartype fully_qualified_namespace: str
    :ivar eventhub_name:
    :vartype eventhub_name: str
    :ivar total_buffered_event_count:
    :vartype total_buffered_event_count: int

    :param str fully_qualified_namespace: The fully qualified host name for the Event Hubs namespace.
     This is likely to be similar to <yournamespace>.servicebus.windows.net
    :param str eventhub_name: The path of the specific Event Hub to connect the client to.
    :param credential: The credential object used for authentication which
     implements a particular interface for getting tokens. It accepts
     :class:`EventHubSharedKeyCredential<azure.eventhub.EventHubSharedKeyCredential>`, or credential objects generated
     by the azure-identity library and objects that implement the `get_token(self, *scopes)` method.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureSasCredential
     or ~azure.core.credentials.AzureNamedKeyCredential
    :keyword bool enable_idempotent_retries:
    :keyword int max_buffered_event_count:
    :keyword int max_wait_time:
    :keyword int max_concurrent_sends_per_partition:
    :keyword on_error:
    :paramtype on_error: Callable[List[~azure.eventhub.EventData], Exception, Optional[str]]
    :keyword on_success:
    :paramtype on_success: Callable[List[~azure.eventhub.EventData], str]
    :keyword executor: A user-specified thread pool. This cannot be combined with
     setting `max_workers`.
    :paramtype executor: Optional[~concurrent.futures.ThreadPoolExecutor]
    :keyword max_workers: Specify the maximum workers in the thread pool. If not
     specified the number used will be derived from the core count of the environment.
     This cannot be combined with `executor`.
    :paramtype max_workers: Optional[int]
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword float auth_timeout: The time in seconds to wait for a token to be authorized by the service.
     The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
    :keyword str user_agent: If specified, this will be added in front of the user agent string.
    :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs. Default
     value is 3.
    :keyword float idle_timeout: Timeout, in seconds, after which this client will close the underlying connection
     if there is no activity. By default the value is None, meaning that the client will not shutdown due to inactivity
     unless initiated by the service.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Event Hubs service. Default is `TransportType.Amqp` in which case port 5671 is used.
     If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
     be used instead which uses port 443 for communication.
    :paramtype transport_type: ~azure.eventhub.TransportType
    :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :keyword str custom_endpoint_address: The custom endpoint address to use for establishing a connection to
     the Event Hubs service, allowing network requests to be routed through any application gateways or
     other paths needed for the host environment. Default is None.
     The format would be like "sb://<custom_endpoint_hostname>:<custom_endpoint_port>".
     If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
    :keyword str connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
     authenticate the identity of the connection endpoint.
     Default is None in which case `certifi.where()` will be used.
    """

    def __init__(
        self,
        fully_qualified_namespace,  # type: str
        eventhub_name,  # type: str
        credential,  # type: Union[AzureSasCredential, TokenCredential, AzureNamedKeyCredential]
        **kwargs  # type: Any
    ):
        # type:(...) -> None
        self.eventhub_name = ''  # type: str
        self.total_buffered_event_count = 0  # type: int

    @classmethod
    def from_connection_string(
        cls,
        conn_str,
        **kwargs
    ):
        # type: (str, Any) -> EventHubBufferedProducerClient
        """

        :param str conn_str: The connection string of an Event Hub.
        :keyword str eventhub_name: The path of the specific Event Hub to connect the client to.
        :keyword bool enable_idempotent_retries:
        :keyword int max_wait_time:
        :keyword int max_buffered_event_count:
        :keyword int max_concurrent_sends_per_partition:
        :keyword on_error:
        :paramtype on_error: Callable[List[~azure.eventhub.EventData], Exception, Optional[str]]
        :keyword on_success:
        :paramtype on_success: Callable[List[~azure.eventhub.EventData], str]
        :keyword executor: A user-specified thread pool. This cannot be combined with
         setting `max_workers`.
        :paramtype executor: Optional[~concurrent.futures.ThreadPoolExecutor]
        :keyword max_workers: Specify the maximum workers in the thread pool. If not
         specified the number used will be derived from the core count of the environment.
         This cannot be combined with `executor`.
        :paramtype max_workers: Optional[int]
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
         Additionally the following keys may also be present: `'username', 'password'`.
        :keyword float auth_timeout: The time in seconds to wait for a token to be authorized by the service.
         The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
        :keyword str user_agent: If specified, this will be added in front of the user agent string.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :keyword float idle_timeout: Timeout, in seconds, after which this client will close the underlying connection
         if there is no activity. By default the value is None, meaning that the client will not shutdown due to
         inactivity unless initiated by the service.
        :keyword transport_type: The type of transport protocol that will be used for communicating with
         the Event Hubs service. Default is `TransportType.Amqp` in which case port 5671 is used.
         If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
         be used instead which uses port 443 for communication.
        :paramtype transport_type: ~azure.eventhub.TransportType
        :keyword str custom_endpoint_address: The custom endpoint address to use for establishing a connection to
         the Event Hubs service, allowing network requests to be routed through any application gateways or
         other paths needed for the host environment. Default is None.
         The format would be like "sb://<custom_endpoint_hostname>:<custom_endpoint_port>".
         If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
        :keyword str connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
         authenticate the identity of the connection endpoint.
         Default is None in which case `certifi.where()` will be used.
        :rtype: ~azure.eventhub.EventHubBufferedProducerClient
        """
        pass

    def enqueue_events(
        self,
        events,
        **kwargs
    ):
        # type: (Union[EventData, List[EventData]], Any) -> None
        """

        :param events:
        :type events: Union[~azure.eventhub.EventData, List[~azure.eventhub.EventData]]
        :keyword str partition_key:
        :keyword str partition_id:
        :keyword int timeout:
        :rtype: None
        """

    def flush(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        """

        :keyword int timeout:
        :rtype: None
        """
        pass

    def get_partition_buffered_event_count(
        self,
        partition_id,
        **kwargs
    ):
        # type: (str, Any) -> int
        """

        :param int partition_id:
        :rtype: int
        """
        pass

    def close(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        """

        :keyword bool abandon_buffered_events:
        :keyword int timeout:
        :rtype: None
        """
