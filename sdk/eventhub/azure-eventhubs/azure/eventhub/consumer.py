# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import uuid
import logging
import time
from typing import List

from uamqp import types, errors
from uamqp import compat
from uamqp import ReceiveClient, Source

from azure.eventhub.common import EventData, EventPosition
from azure.eventhub.error import EventHubError, AuthenticationError, ConnectError, ConnectionLostError, _error_handler


log = logging.getLogger(__name__)


class EventHubConsumer(object):
    """
    A consumer responsible for reading EventData from a specific Event Hub
     partition and as a member of a specific consumer group.

    A consumer may be exclusive, which asserts ownership over the partition for the consumer
     group to ensure that only one consumer from that group is reading the from the partition.
     These exclusive consumers are sometimes referred to as "Epoch Consumers."

    A consumer may also be non-exclusive, allowing multiple consumers from the same consumer
     group to be actively reading events from the partition.  These non-exclusive consumers are
     sometimes referred to as "Non-Epoch Consumers."

    """
    timeout = 0
    _epoch = b'com.microsoft:epoch'

    def __init__(self, client, source, event_position=None, prefetch=300, owner_level=None,
                 keep_alive=None, auto_reconnect=True):
        """
        Instantiate a consumer. EventHubConsumer should be instantiated by calling the `create_consumer` method
         in EventHubClient.

        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.client.EventHubClient
        :param source: The source EventHub from which to receive events.
        :type source: str
        :param prefetch: The number of events to prefetch from the service
         for processing. Default is 300.
        :type prefetch: int
        :param owner_level: The priority of the exclusive consumer. It will an exclusive
         consumer if owner_level is set.
        :type owner_level: int
        """
        self.running = False
        self.client = client
        self.source = source
        self.offset = event_position
        self.messages_iter = None
        self.prefetch = prefetch
        self.owner_level = owner_level
        self.keep_alive = keep_alive
        self.auto_reconnect = auto_reconnect
        self.retry_policy = errors.ErrorPolicy(max_retries=self.client.config.max_retries, on_error=_error_handler)
        self.reconnect_backoff = 1
        self.properties = None
        self.redirected = None
        self.error = None
        partition = self.source.split('/')[-1]
        self.name = "EHReceiver-{}-partition{}".format(uuid.uuid4(), partition)
        source = Source(self.source)
        if self.offset is not None:
            source.set_filter(self.offset._selector())  # pylint: disable=protected-access
        if owner_level:
            self.properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(owner_level))}
        self._handler = ReceiveClient(
            source,
            auth=self.client.get_auth(),
            debug=self.client.config.network_tracing,
            prefetch=self.prefetch,
            link_properties=self.properties,
            timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client._create_properties(self.client.config.user_agent))  # pylint: disable=protected-access

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_val)

    def __iter__(self):
        return self

    def __next__(self):
        self._open()
        max_retries = self.client.config.max_retries
        connecting_count = 0
        while True:
            connecting_count += 1
            try:
                if not self.messages_iter:
                    self.messages_iter = self._handler.receive_messages_iter()
                message = next(self.messages_iter)
                event_data = EventData(message=message)
                self.offset = EventPosition(event_data.offset, inclusive=False)
                return event_data
            except errors.AuthenticationException as auth_error:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer disconnected due to token error. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer authentication failed. Shutting down.")
                    error = AuthenticationError(str(auth_error), auth_error)
                    self.close(auth_error)
                    raise error
            except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
                if shutdown.action.retry and self.auto_reconnect:
                    log.info("EventHubConsumer detached. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(exception=error)
                    raise error
            except errors.MessageHandlerError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer detached. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(error)
                    raise error
            except errors.AMQPConnectionError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer connection lost. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer connection lost. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(error)
                    raise error
            except compat.TimeoutException as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer timed out receiving event data. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer timed out. Shutting down.")
                    self.close(shutdown)
                    raise ConnectionLostError(str(shutdown), shutdown)
            except StopIteration:
                raise
            except KeyboardInterrupt:
                log.info("EventHubConsumer stops due to keyboard interrupt")
                self.close()
                raise
            except Exception as e:
                log.error("Unexpected error occurred (%r). Shutting down.", e)
                error = EventHubError("Receive failed: {}".format(e), e)
                self.close(exception=error)
                raise error

    def _check_closed(self):
        if self.error:
            raise EventHubError("This consumer has been closed. Please create a new consumer to receive event data.",
                                self.error)

    def _redirect(self, redirect):
        self.redirected = redirect
        self.running = False
        self.messages_iter = None
        self._open()

    def _open(self):
        """
        Open the EventHubConsumer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        # pylint: disable=protected-access
        self._check_closed()
        if self.redirected:
            self.client._process_redirect_uri(self.redirected)
            self.source = self.redirected.address
            source = Source(self.source)
            if self.offset is not None:
                source.set_filter(self.offset._selector())

            alt_creds = {
                "username": self.client._auth_config.get("iot_username"),
                "password":self.client._auth_config.get("iot_password")}
            self._handler = ReceiveClient(
                source,
                auth=self.client.get_auth(**alt_creds),
                debug=self.client.config.network_tracing,
                prefetch=self.prefetch,
                link_properties=self.properties,
                timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client._create_properties(self.client.config.user_agent))  # pylint: disable=protected-access
        if not self.running:
            self._connect()
            self.running = True

    def _connect(self):
        connected = self._build_connection()
        if not connected:
            time.sleep(self.reconnect_backoff)
            while not self._build_connection(is_reconnect=True):
                time.sleep(self.reconnect_backoff)

    def _build_connection(self, is_reconnect=False):
        """

        :param is_reconnect: True - trying to reconnect after fail to connect or a connection is lost.
                             False - the 1st time to connect
        :return: True - connected.  False - not connected
        """
        # pylint: disable=protected-access
        if is_reconnect:
            alt_creds = {
                "username": self.client._auth_config.get("iot_username"),
                "password": self.client._auth_config.get("iot_password")}
            self._handler.close()
            source = Source(self.source)
            if self.offset is not None:
                source.set_filter(self.offset._selector())
            self._handler = ReceiveClient(
                source,
                auth=self.client.get_auth(**alt_creds),
                debug=self.client.config.network_tracing,
                prefetch=self.prefetch,
                link_properties=self.properties,
                timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client._create_properties(
                    self.client.config.user_agent))  # pylint: disable=protected-access
            self.messages_iter = None
        try:
            self._handler.open()
            while not self._handler.client_ready():
                time.sleep(0.05)
            return True
        except errors.AuthenticationException as shutdown:
            if is_reconnect:
                log.info("EventHubConsumer couldn't authenticate. Shutting down. (%r)", shutdown)
                error = AuthenticationError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
            else:
                log.info("EventHubConsumer couldn't authenticate. Attempting reconnect.")
                return False
        except errors.LinkRedirect as redirect:
            self._redirect(redirect)
            return True
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry:
                log.info("EventHubConsumer detached. Attempting reconnect.")
                return False
            else:
                log.info("EventHubConsumer detached. Shutting down.")
                error = ConnectError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if is_reconnect:
                log.info("EventHubConsumer detached. Shutting down.")
                error = ConnectError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
            else:
                log.info("EventHubConsumer detached. Attempting reconnect.")
                return False
        except errors.AMQPConnectionError as shutdown:
            if is_reconnect:
                log.info("EventHubConsumer connection error (%r). Shutting down.", shutdown)
                error = AuthenticationError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
            else:
                log.info("EventHubConsumer couldn't authenticate. Attempting reconnect.")
                return False
        except compat.TimeoutException as shutdown:
            if is_reconnect:
                log.info("EventHubConsumer authentication timed out. Shutting down.")
                error = AuthenticationError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
            else:
                log.info("EventHubConsumer authentication timed out. Attempting reconnect.")
                return False
        except Exception as e:
            log.error("Unexpected error occurred when building connection (%r). Shutting down.", e)
            error = EventHubError("Unexpected error occurred when building connection", e)
            self.close(exception=error)
            raise error

    def _reconnect(self):
        return self._build_connection(is_reconnect=True)

    @property
    def queue_size(self):
        # type:() -> int
        """
        The current size of the unprocessed Event queue.

        :rtype: int
        """
        # pylint: disable=protected-access
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    def receive(self, max_batch_size=None, timeout=None):
        # type:(int, float) -> List[EventData]
        """
        Receive events from the EventHub.

        :param max_batch_size: Receive a batch of events. Batch size will
         be up to the maximum specified, but will return as soon as service
         returns no new events. If combined with a timeout and no events are
         retrieve before the time, the result will be empty. If no batch
         size is supplied, the prefetch size will be the maximum.
        :type max_batch_size: int
        :param timeout: The maximum wait time to build up the requested message count for the batch.
         If not specified, the default wait time specified when the consumer was created will be used.
        :type timeout: float
        :rtype: list[~azure.eventhub.common.EventData]
        :raises: ~azure.eventhub.AuthenticationError, ~azure.eventhub.ConnectError, ~azure.eventhub.ConnectionLostError,
                ~azure.eventhub.EventHubError
        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_sync_receive]
                :end-before: [END eventhub_client_sync_receive]
                :language: python
                :dedent: 4
                :caption: Receive events from the EventHub.

        """
        self._check_closed()
        self._open()

        max_batch_size = min(self.client.config.max_batch_size, self.prefetch) if max_batch_size is None else max_batch_size
        timeout = self.client.config.receive_timeout if timeout is None else timeout

        data_batch = []  # type: List[EventData]
        max_retries = self.client.config.max_retries
        connecting_count = 0
        while True:
            connecting_count += 1
            try:
                timeout_ms = 1000 * timeout if timeout else 0
                message_batch = self._handler.receive_message_batch(
                    max_batch_size=max_batch_size - (len(data_batch) if data_batch else 0),
                    timeout=timeout_ms)
                for message in message_batch:
                    event_data = EventData(message=message)
                    self.offset = EventPosition(event_data.offset)
                    data_batch.append(event_data)
                return data_batch
            except errors.AuthenticationException as auth_error:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer disconnected due to token error. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer authentication failed. Shutting down.")
                    error = AuthenticationError(str(auth_error), auth_error)
                    self.close(auth_error)
                    raise error
            except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
                if shutdown.action.retry and self.auto_reconnect:
                    log.info("EventHubConsumer detached. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(exception=error)
                    raise error
            except errors.MessageHandlerError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer detached. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(error)
                    raise error
            except errors.AMQPConnectionError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer connection lost. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer connection lost. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(error)
                    raise error
            except compat.TimeoutException as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubConsumer timed out receiving event data. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubConsumer timed out. Shutting down.")
                    self.close(shutdown)
                    raise ConnectionLostError(str(shutdown), shutdown)
            except KeyboardInterrupt:
                log.info("EventHubConsumer stops due to keyboard interrupt")
                self.close()
                raise
            except Exception as e:
                log.error("Unexpected error occurred (%r). Shutting down.", e)
                error = EventHubError("Receive failed: {}".format(e), e)
                self.close(exception=error)
                raise error

    def close(self, exception=None):
        # type:(Exception) -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_receiver_close]
                :end-before: [END eventhub_client_receiver_close]
                :language: python
                :dedent: 4
                :caption: Close down the handler.

        """
        if self.messages_iter:
            self.messages_iter.close()
            self.messages_iter = None
        self.running = False
        if self.error:
            return
        if isinstance(exception, errors.LinkRedirect):
            self.redirected = exception
        elif isinstance(exception, EventHubError):
            self.error = exception
        elif exception:
            self.error = EventHubError(str(exception))
        else:
            self.error = EventHubError("This receive handler is now closed.")
        self._handler.close()

    next = __next__  # for python2.7
