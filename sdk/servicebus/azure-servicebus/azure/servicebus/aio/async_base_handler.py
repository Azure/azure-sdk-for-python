# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import logging
from urllib.parse import urlparse

from uamqp import AMQPClientAsync
from uamqp.message import Message, MessageProperties
from uamqp import authentication
from uamqp import constants, errors

from azure.servicebus.common.constants import ASSOCIATEDLINKPROPERTYNAME
from azure.servicebus.common.utils import create_properties, get_running_loop
from azure.servicebus.common.errors import (
    _ServiceBusErrorPolicy,
    ServiceBusError,
    ServiceBusConnectionError,
    InvalidHandlerState,
    ServiceBusAuthorizationError)


_log = logging.getLogger(__name__)


class BaseHandler:  # pylint: disable=too-many-instance-attributes

    def __init__(self, endpoint, auth_config, *, loop=None, connection=None, encoding='UTF-8', debug=False, **kwargs):
        self.loop = loop or get_running_loop()
        self.running = False
        self.error = None
        self.endpoint = endpoint
        self.entity = urlparse(endpoint).path.strip('/')
        self.mgmt_target = self.entity + "/$management"
        self.debug = debug
        self.encoding = encoding
        self.auth_config = auth_config
        self.connection = connection
        self.auto_reconnect = kwargs.pop('auto_reconnect', True)
        self.properties = create_properties()
        self.error_policy = kwargs.pop('error_policy', None)
        self.handler_kwargs = kwargs
        if not self.error_policy:
            max_retries = kwargs.pop('max_message_retries', 3)
            is_session = hasattr(self, 'session_id')
            self.error_policy = _ServiceBusErrorPolicy(max_retries=max_retries, is_session=is_session)
        self._handler = None
        self._build_handler()

    async def __aenter__(self):
        """Open the handler in a context manager."""
        await self.open()
        return self

    async def __aexit__(self, *args):
        """Close the handler when exiting a context manager."""
        await self.close()

    def _build_handler(self):
        auth = None if self.connection else authentication.SASTokenAsync.from_shared_access_key(**self.auth_config)
        self._handler = AMQPClientAsync(
            self.endpoint,
            loop=self.loop,
            auth=auth,
            debug=self.debug,
            properties=self.properties,
            error_policy=self.error_policy,
            encoding=self.encoding,
            **self.handler_kwargs)

    async def _mgmt_request_response(self, operation, message, callback, keep_alive_associated_link=True, **kwargs):
        if not self.running:
            raise InvalidHandlerState("Client connection is closed.")

        application_properties = {}
        if keep_alive_associated_link:
            try:
                application_properties = {ASSOCIATEDLINKPROPERTYNAME:self._handler.message_handler.name}
            except AttributeError:
                pass

        mgmt_msg = Message(
            body=message,
            properties=MessageProperties(
                reply_to=self.mgmt_target,
                encoding=self.encoding,
                **kwargs),
            application_properties=application_properties)
        try:
            return await self._handler.mgmt_request_async(
                mgmt_msg,
                operation,
                op_type=b"entity-mgmt",
                node=self.mgmt_target.encode(self.encoding),
                timeout=5000,
                callback=callback)
        except Exception as exp:  # pylint: disable=broad-except
            raise ServiceBusError("Management request failed: {}".format(exp), exp)

    async def _handle_exception(self, exception):
        if isinstance(exception, (errors.LinkDetach, errors.ConnectionClose)):
            if exception.action and exception.action.retry and self.auto_reconnect:
                _log.info("Async handler detached. Attempting reconnect.")
                await self.reconnect()
            elif exception.condition == constants.ErrorCodes.UnauthorizedAccess:
                _log.info("Async handler detached. Shutting down.")
                error = ServiceBusAuthorizationError(str(exception), exception)
                await self.close(exception=error)
                raise error
            else:
                _log.info("Async handler detached. Shutting down.")
                error = ServiceBusConnectionError(str(exception), exception)
                await self.close(exception=error)
                raise error
        elif isinstance(exception, errors.MessageHandlerError):
            if self.auto_reconnect:
                _log.info("Async handler error. Attempting reconnect.")
                await self.reconnect()
            else:
                _log.info("Async handler error. Shutting down.")
                error = ServiceBusConnectionError(str(exception), exception)
                await self.close(exception=error)
                raise error
        elif isinstance(exception, errors.AMQPConnectionError):
            message = "Failed to open handler: {}".format(exception)
            raise ServiceBusConnectionError(message, exception)
        else:
            _log.info("Unexpected error occurred (%r). Shutting down.", exception)
            error = ServiceBusError("Handler failed: {}".format(exception), exception)
            await self.close(exception=error)
            raise error

    async def reconnect(self):
        """Reconnect the handler.

        If the handler was disconnected from the service with
        a retryable error - attempt to reconnect.
        This method will be called automatically for most retryable errors.
        """
        await self._handler.close_async()
        self.running = False
        self._build_handler()
        await self.open()

    async def open(self):
        """Open handler connection and authenticate session.

        If the handler is already open, this operation will do nothing.
        A handler opened with this method must be explicitly closed.
        It is recommended to open a handler within a context manager as
        opposed to calling the method directly.

        .. note:: This operation is not thread-safe.

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START open_close_sender_directly]
                :end-before: [END open_close_sender_directly]
                :language: python
                :dedent: 4
                :caption: Explicitly open and close a Sender.

        """
        if self.running:
            return
        self.running = True
        try:
            await self._handler.open_async(connection=self.connection)
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                await self._handle_exception(e)
            except:
                self.running = False
                raise

    async def close(self, exception=None):
        """Close down the handler connection.

        If the handler has already closed,
        this operation will do nothing. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.
        It is recommended to open a handler within a context manager as
        opposed to calling the method directly.

        .. note:: This operation is not thread-safe.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START open_close_sender_directly]
                :end-before: [END open_close_sender_directly]
                :language: python
                :dedent: 4
                :caption: Explicitly open and close a Sender.

        """
        self.running = False
        if self.error:
            return
        if isinstance(exception, ServiceBusError):
            self.error = exception
        elif exception:
            self.error = ServiceBusError(str(exception))
        else:
            self.error = ServiceBusError("This message handler is now closed.")
        await self._handler.close_async()
