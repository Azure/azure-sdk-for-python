# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
import datetime
import time

from uamqp import ReceiveClient, Source

from ._client_base import ClientBase
from .common.constants import (
    ReceiveSettleMode,
    NEXT_AVAILABLE,
    SESSION_LOCKED_UNTIL,
    DATETIMEOFFSET_EPOCH,
    SESSION_FILTER
)
from .common.errors import (
    _ServiceBusErrorPolicy
)
from .common.utils import create_properties
from .common.message import Message


class SessionMixin(object):  # pylint: disable=too-few-public-methods

    def _get_source(self):
        source = Source(self._entity_uri)
        session_filter = None if self._session == NEXT_AVAILABLE else self._session
        source.set_filter(session_filter, name=SESSION_FILTER, descriptor=None)
        return source

    def _on_attach(self, source, target, properties, error):  # pylint: disable=unused-argument
        if str(source) == self.endpoint:
            self.session_start = datetime.datetime.now()
            expiry_in_seconds = properties.get(SESSION_LOCKED_UNTIL)
            if expiry_in_seconds:
                expiry_in_seconds = (expiry_in_seconds - DATETIMEOFFSET_EPOCH)/10000000
                self.locked_until = datetime.datetime.fromtimestamp(expiry_in_seconds)
            session_filter = source.get_filter(name=SESSION_FILTER)
            self.session_id = session_filter.decode(self.encoding)

    @property
    def expired(self):
        """Whether the receivers lock on a particular session has expired.

        :rtype: bool
        """
        if self.locked_until and self.locked_until <= datetime.datetime.now():
            return True
        return False


class ServiceBusReceiverClient(ClientBase, SessionMixin):
    def __init__(
        self,
        fully_qualified_namespace,
        entity_name,
        credential,
        **kwargs
    ):
        # type: (str, str, TokenCredential, Any) -> None
        super(ServiceBusReceiverClient, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            entity_name=entity_name,
            **kwargs
        )

        if kwargs.get("subscription_name"):
            self.subscription_name = kwargs.get("subscription_name")
            self._is_subscription = True
            self._entity_path = entity_name + "/Subscriptions/" + self.subscription_name
        else:
            self._entity_path = entity_name

        self._session = kwargs.get("session")
        self._auth_uri = "sb://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._entity_uri = "amqps://{}/{}".format(self.fully_qualified_namespace, self._entity_path)
        self._logging_enable = self._config.logging_enable
        self._mode = kwargs.get("mode", ReceiveSettleMode.PeekLock)
        self._error_policy = _ServiceBusErrorPolicy(
            max_retries=self._config.retry_total,
            is_session=(True if self._session else False)
        )
        self._error = None
        self._name = "SBReceiver-{}".format(uuid.uuid4())
        self._create_handler()

    def __iter__(self):
        return self

    def __next__(self):
        pass

    def _create_handler(self):
        auth = self._create_auth()
        properties = create_properties()
        if not self._session:
            self._handler = ReceiveClient(
                self._entity_uri,
                auth=auth,
                debug=self._logging_enable,
                properties=properties,
                error_policy=self._error_policy,
                client_name=self._name,
                auto_complete=False,
                encoding=self._config.encoding,
                receive_settle_mode=self._mode.value
            )
        else:
            self._handler = ReceiveClient(
                self._get_source(),
                auth=auth,
                debug=self._logging_enable,
                properties=properties,
                error_policy=self._error_policy,
                client_name=self._name,
                on_attach=self._on_attach,
                auto_complete=False,
                encoding=self._config.encoding,
                receive_settle_mode=self._mode.value
            )

    def _open(self):
        if self._running:
            return
        self._running = True
        try:
            self._handler.open()
            self._message_iter = self._handler.receive_messages_iter()
            while not self._handler.auth_complete():
                time.sleep(0.05)
            while not self._handler.client_ready():
                time.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                self._handle_exception(e)
            except Exception:
                self.running = False
                raise

    def _build_message(self, received):
        message = Message(None, message=received)
        message._receiver = self  # pylint: disable=protected-access
        self._last_received_sequenced_number = message.sequence_number
        return message

    def next(self):
        pass

    def close(self, exception=None):
        if not self._running:
            return
        self._running = False
        super(ServiceBusReceiverClient, self).close(exception=exception)

    @classmethod
    def from_queue(
        cls,
        fully_qualified_namespace,
        queue_name,
        credential,
        **kwargs
    ):
        # type: (str, str, TokenCredential, Any) -> ServiceBusReceiverClient
        return cls(
            fully_qualified_namespace=fully_qualified_namespace,
            entity_name=queue_name,
            credential=credential,
            **kwargs
        )

    @classmethod
    def from_topic_subscription(
        cls,
        fully_qualified_namespace,
        topic_name,
        subscription_name,
        credential,
        **kwargs
    ):
        # type: (str, str, str, TokenCredential, Any) -> ServiceBusReceiverClient
        return cls(
            fully_qualified_namespace=fully_qualified_namespace,
            entity_name=topic_name,
            subscription_name=subscription_name,
            credential=credential,
            **kwargs
        )

    @classmethod
    def from_connection_string(
        cls,
        conn_str,
        **kwargs,
    ):
        # type: (str, Any) -> ServiceBusReceiverClient
        constructor_args = cls._from_connection_string(
            conn_str,
            **kwargs
        )
        return cls(**constructor_args)

    def receive(self, max_batch_size=None, timeout=None):
        self._open()
        wrapped_batch = []
        max_batch_size = max_batch_size or self._handler._prefetch  # pylint: disable=protected-access
        try:
            timeout_ms = 1000 * timeout if timeout else 0
            batch = self._handler.receive_message_batch(
                max_batch_size=max_batch_size,
                timeout=timeout_ms)
            for received in batch:
                message = self._build_message(received)
                wrapped_batch.append(message)
        except Exception as e:  # pylint: disable=broad-except
            self._handle_exception(e)
        return wrapped_batch




