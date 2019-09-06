# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import time

from uamqp import errors, constants, compat  # type: ignore
from azure.eventhub.error import EventHubError, _handle_exception

log = logging.getLogger(__name__)


class ConsumerProducerMixin(object):
    def __init__(self):
        self._client = None
        self._handler = None
        self._name = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_val)

    def _check_closed(self):
        if self._error:
            raise EventHubError("{} has been closed. Please create a new one to handle event data.".format(self._name))

    def _create_handler(self):
        pass

    def _redirect(self, redirect):
        self._redirected = redirect
        self._running = False
        self._close_connection()

    def _open(self):
        """
        Open the EventHubConsumer/EventHubProducer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        # pylint: disable=protected-access
        if not self._running:
            if self._handler:
                self._handler.close()
            if self._redirected:
                alt_creds = {
                    "username": self._client._auth_config.get("iot_username"),
                    "password": self._client._auth_config.get("iot_password")}
            else:
                alt_creds = {}
            self._create_handler()
            self._handler.open(connection=self._client._conn_manager.get_connection(  # pylint: disable=protected-access
                self._client._address.hostname,
                self._client._get_auth(**alt_creds)
            ))
            while not self._handler.client_ready():
                time.sleep(0.05)
            self._max_message_size_on_link = self._handler.message_handler._link.peer_max_message_size \
                                             or constants.MAX_MESSAGE_LENGTH_BYTES  # pylint: disable=protected-access
            self._running = True

    def _close_handler(self):
        self._handler.close()  # close the link (sharing connection) or connection (not sharing)
        self._running = False

    def _close_connection(self):
        self._close_handler()
        self._client._conn_manager.reset_connection_if_broken()  # pylint: disable=protected-access

    def _handle_exception(self, exception):
        if not self._running and isinstance(exception, compat.TimeoutException):
            exception = errors.AuthenticationException("Authorization timeout.")
            return _handle_exception(exception, self)

        return _handle_exception(exception, self)

    def _do_retryable_operation(self, operation, timeout=100000, **kwargs):
        # pylint:disable=protected-access
        timeout_time = time.time() + (
            timeout if timeout else 100000)  # timeout equals to 0 means no timeout, set the value to be a large number.
        retried_times = 0
        last_exception = kwargs.pop('last_exception', None)
        operation_need_param = kwargs.pop('operation_need_param', True)

        while retried_times <= self._client._config.max_retries:  # pylint: disable=protected-access
            try:
                if operation_need_param:
                    return operation(timeout_time=timeout_time, last_exception=last_exception, **kwargs)
                return operation()
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = self._handle_exception(exception)
                self._client._try_delay(retried_times=retried_times, last_exception=last_exception,
                                        timeout_time=timeout_time, entity_name=self._name)
                retried_times += 1

        log.info("%r operation has exhausted retry. Last exception: %r.", self._name, last_exception)
        raise last_exception

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
        self._running = False
        if self._error:  # type: ignore
            return
        if isinstance(exception, errors.LinkRedirect):
            self._redirected = exception
        elif isinstance(exception, EventHubError):
            self._error = exception
        elif exception:
            self._error = EventHubError(str(exception))
        else:
            self._error = EventHubError("{} handler is closed.".format(self._name))
        if self._handler:
            self._handler.close()  # this will close link if sharing connection. Otherwise close connection
