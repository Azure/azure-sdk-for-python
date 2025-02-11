import functools
import time
import warnings
import datetime
from ._pyamqp import AMQPClient
from ._pyamqp.constants import SenderSettleMode
from typing import TYPE_CHECKING, Any, Optional, Union
from ._common.utils import create_authentication
from azure.servicebus._common.constants import (
    MGMT_REQUEST_SKIP,
    MGMT_REQUEST_TOP,
    MGMT_REQUEST_LAST_UPDATED_TIME,
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
    ServiceBusReceiveMode,
)
from ._common.tracing import (
    get_receive_links,
    receive_trace_context_manager,
    SPAN_NAME_SESSIONS
)
from azure.servicebus._common.receiver_mixins import ReceiverMixin
from ._servicebus_session import ServiceBusSession
from ._base_handler import BaseHandler
from ._common import mgmt_handlers

if TYPE_CHECKING:
    from azure.core.credentials import (
        TokenCredential,
        AzureSasCredential,
        AzureNamedKeyCredential,
    )


class ServiceBusManagementOperationClient(BaseHandler, ReceiverMixin):

    def __init__(
        self,
        fully_qualified_namespace: str,
        credential: Union["TokenCredential", "AzureSasCredential", "AzureNamedKeyCredential"],
        *,
        entity_name: str,
        **kwargs: Any,
    ) -> None:
        super(ServiceBusManagementOperationClient, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace, credential=credential, entity_name=entity_name, **kwargs
    )
        self._session = None
        self._max_message_size_on_link = 0
        self._max_batch_size_on_link = 0
        self._populate_attributes(
            entity_name=entity_name,
            **kwargs,
        )
        self._connection = kwargs.get("connection")
        self._handler

    def __enter__(self) -> "ServiceBusManagementOperationClient":
        if self._shutdown.is_set():
            raise ValueError(
                "The handler has already been shutdown. Please use ServiceBusClient to create a new instance."
            )

        self._open_with_retry()
        return self

    @classmethod
    def _from_connection_string(cls, conn_str: str, **kwargs: Any # pylint: disable=docstring-keyword-should-match-keyword-only
                                )-> "ServiceBusManagementOperationClient":
        """Create a ServiceBusManagementOperation from a connection string.
        """
        constructor_args = cls._convert_connection_string_to_kwargs(conn_str, **kwargs)
        return cls(**constructor_args)

    def _create_handler(self, auth):
        self._handler = self._amqp_transport.create_amqp_client(
            config=self._config,
            target=self._entity_uri,
            auth=auth,
            properties=self._properties,
            retry_policy=self._error_policy,
            client_name=self._name,
        )

    def _open(self):
        # pylint: disable=protected-access
        if self._running:
            return
        if self._handler and not self._handler._shutdown:
            self._handler.close()

        auth = None if self._connection else create_authentication(self)
        self._create_handler(auth)
        try:
            self._handler.open(connection=self._connection)
            while not self._handler.client_ready():
                time.sleep(0.05)
            self._running = True
        except:
            self._close_handler()
            raise

        if self._auto_lock_renewer and self._session:
            self._auto_lock_renewer.register(self, self.session)

    def _close_handler(self):
        self._message_iter = None
        super(ServiceBusManagementOperationClient, self)._close_handler()

    def close(self):
        # type: () -> None
        super(ServiceBusManagementOperationClient, self).close()
        self._message_iter = None  # pylint: disable=attribute-defined-outside-init

    def get_sessions(
        self,
        *,
        last_updated_time: datetime.datetime = datetime.datetime.max,
        skip_num_sessions: int = 0,
        max_num_sessions: int = 1,
        timeout: Optional[float] = None,
        **kwargs
    ):
        """Get sessions from the Service Bus entity.
        :keyword last_updated_time: Filter sessions based on the last updated time.
        :paramtype last_updated_time: datetime.datetime
        :keyword skip_num_sessions: Skip this number of sessions.
        :paramtype skip_num_sessions: int
        :keyword max_num_sessions: Maximum number of sessions to return.
        :paramtype max_num_sessions: int
        :return: List of session ids.
        :rtype: List[str]
        """
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        self._check_live()
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")

        self._open()
        message = {
            MGMT_REQUEST_LAST_UPDATED_TIME: last_updated_time,
            MGMT_REQUEST_SKIP: skip_num_sessions,
            MGMT_REQUEST_TOP: max_num_sessions,
        }

        handler = functools.partial(mgmt_handlers.list_sessions_op, amqp_transport=self._amqp_transport)
        start_time = time.time_ns()
        messages = self._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION, message, handler, timeout=timeout
        )
        links = get_receive_links(messages)
        with receive_trace_context_manager(self, span_name=SPAN_NAME_SESSIONS, links=links, start_time=start_time):
            return messages