# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import time
import logging
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from uamqp import AMQPClient
from uamqp import authentication
from uamqp import constants, errors
from uamqp.message import Message, MessageProperties

from azure.servicebus.common.constants import ASSOCIATEDLINKPROPERTYNAME
from azure.servicebus.common.utils import create_properties
from azure.servicebus.common.errors import (
    _ServiceBusErrorPolicy,
    InvalidHandlerState,
    ServiceBusError,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError)


_log = logging.getLogger(__name__)


class BaseHandler(object):  # pylint: disable=too-many-instance-attributes

    def __init__(self, endpoint, auth_config, connection=None, encoding='UTF-8', debug=False, **kwargs):
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

    def __enter__(self):
        """Open the handler in a context manager."""
        self.open()
        return self

    def __exit__(self, *args):
        """Close the handler when exiting a context manager."""
        self.close()

    def _build_handler(self):
        auth = None if self.connection else authentication.SASTokenAuth.from_shared_access_key(**self.auth_config)
        self._handler = AMQPClient(
            self.endpoint,
            auth=auth,
            debug=self.debug,
            properties=self.properties,
            error_policy=self.error_policy,
            encoding=self.encoding,
            **self.handler_kwargs)

    def _mgmt_request_response(self, operation, message, callback, keep_alive_associated_link=True, **kwargs):
        if not self.running:
            raise InvalidHandlerState("Client connection is closed.")

        application_properties = {}
        # Some mgmt calls do not support an associated link name.  Most do, however, so on by default.
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
            return self._handler.mgmt_request(
                mgmt_msg,
                operation,
                op_type=b"entity-mgmt",
                node=self.mgmt_target.encode(self.encoding),
                timeout=5000,
                callback=callback)
        except Exception as exp:  # pylint: disable=broad-except
            raise ServiceBusError("Management request failed: {}".format(exp), exp)

    def _handle_exception(self, exception):
        if isinstance(exception, (errors.LinkDetach, errors.ConnectionClose)):
            if exception.action and exception.action.retry and self.auto_reconnect:
                _log.info("Handler detached. Attempting reconnect.")
                self.reconnect()
            elif exception.condition == constants.ErrorCodes.UnauthorizedAccess:
                _log.info("Handler detached. Shutting down.")
                error = ServiceBusAuthorizationError(str(exception), exception)
                self.close(exception=error)
                raise error
            else:
                _log.info("Handler detached. Shutting down.")
                error = ServiceBusConnectionError(str(exception), exception)
                self.close(exception=error)
                raise error
        elif isinstance(exception, errors.MessageHandlerError):
            if self.auto_reconnect:
                _log.info("Handler error. Attempting reconnect.")
                self.reconnect()
            else:
                _log.info("Handler error. Shutting down.")
                error = ServiceBusConnectionError(str(exception), exception)
                self.close(exception=error)
                raise error
        elif isinstance(exception, errors.AMQPConnectionError):
            message = "Failed to open handler: {}".format(exception)
            raise ServiceBusConnectionError(message, exception)
        else:
            _log.info("Unexpected error occurred (%r). Shutting down.", exception)
            error = ServiceBusError("Handler failed: {}".format(exception))
            self.close(exception=error)
            raise error

    def reconnect(self):
        """Reconnect the handler.

        If the handler was disconnected from the service with
        a retryable error - attempt to reconnect.
        This method will be called automatically for most retryable errors.
        """
        self._handler.close()
        self.running = False
        self._build_handler()
        self.open()

    def open(self):
        """Open handler connection and authenticate session.

        If the handler is already open, this operation will do nothing.
        A handler opened with this method must be explicitly closed.
        It is recommended to open a handler within a context manager as
        opposed to calling the method directly.

        .. note:: This operation is not thread-safe.

        """
        if self.running:
            return
        self.running = True
        try:
            self._handler.open(connection=self.connection)
            while not self._handler.client_ready():
                time.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                self._handle_exception(e)
            except:
                self.running = False
                raise

    def close(self, exception=None):
        """Close down the handler connection.

        If the handler has already closed, this operation will do nothing. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.
        It is recommended to open a handler within a context manager as
        opposed to calling the method directly.

        .. note:: This operation is not thread-safe.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception
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
        self._handler.close()
