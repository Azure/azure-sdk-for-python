#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# pylint: disable=no-member

import logging
import sys

from uamqp import c_uamqp  # pylint: disable=import-self

from uamqp.message import Message, BatchMessage
from uamqp.address import Source, Target

from uamqp.connection import Connection
from uamqp.session import Session
from uamqp.client import AMQPClient, SendClient, ReceiveClient
from uamqp.sender import MessageSender
from uamqp.receiver import MessageReceiver
from uamqp.constants import TransportType

try:
    from uamqp.async_ops import ConnectionAsync
    from uamqp.async_ops import SessionAsync
    from uamqp.async_ops import MessageSenderAsync
    from uamqp.async_ops import MessageReceiverAsync
    from uamqp.async_ops.client_async import (
        AMQPClientAsync,
        SendClientAsync,
        ReceiveClientAsync,
        AsyncMessageIter)
except (SyntaxError, ImportError):
    pass  # Async not supported.


__version__ = "1.2.8"


_logger = logging.getLogger(__name__)
_is_win = sys.platform.startswith('win')
c_uamqp.set_python_logger()


def send_message(target, data, auth=None, debug=False):
    """Send a single message to AMQP endpoint.

    :param target: The target AMQP endpoint.
    :type target: str, bytes or ~uamqp.address.Target
    :param data: The contents of the message to send.
    :type data: str, bytes or ~uamqp.message.Message
    :param auth: The authentication credentials for the endpoint.
     This should be one of the subclasses of uamqp.authentication.AMQPAuth. Currently
     this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param debug: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :type debug: bool
    :return: A list of states for each message sent.
    :rtype: list[~uamqp.constants.MessageState]
    """
    message = data if isinstance(data, Message) else Message(body=data)
    with SendClient(target, auth=auth, debug=debug) as send_client:
        send_client.queue_message(message)  # pylint: disable=no-member
        return send_client.send_all_messages()  # pylint: disable=no-member


def receive_message(source, auth=None, timeout=0, debug=False):
    """Receive a single message from an AMQP endpoint.

    :param source: The AMQP source endpoint to receive from.
    :type source: str, bytes or ~uamqp.address.Source
    :param auth: The authentication credentials for the endpoint.
     This should be one of the subclasses of uamqp.authentication.AMQPAuth. Currently
     this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param timeout: The timeout in milliseconds after which to return None if no messages
     are retrieved. If set to `0` (the default), the receiver will not timeout and
     will continue to wait for messages until interrupted.
    :param debug: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :type debug: bool
    :rtype: ~uamqp.message.Message or None
    """
    received = receive_messages(source, auth=auth, max_batch_size=1, timeout=timeout, debug=debug)
    if received:
        return received[0]
    return None


def receive_messages(source, auth=None, max_batch_size=None, timeout=0, debug=False, **kwargs):
    """Receive a batch of messages from an AMQP endpoint.

    :param source: The AMQP source endpoint to receive from.
    :type source: str, bytes or ~uamqp.address.Source
    :param auth: The authentication credentials for the endpoint.
     This should be one of the subclasses of ~uamqp.authentication.AMQPAuth. Currently
     this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param max_batch_size: The maximum number of messages to return in a batch. If the
     receiver receives a smaller number than this, it will not wait to return them so
     the actual number returned can be anything up to this value. If the receiver reaches
     a timeout, an empty list will be returned.
    :param timeout: The timeout in milliseconds after which to return if no messages
     are retrieved. If set to `0` (the default), the receiver will not timeout and
     will continue to wait for messages until interrupted.
    :param debug: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :type debug: bool
    :rtype: list[~uamqp.message.Message]
    """
    if max_batch_size:
        kwargs['prefetch'] = max_batch_size
    with ReceiveClient(source, auth=auth, debug=debug, **kwargs) as receive_client:
        return receive_client.receive_message_batch(  # pylint: disable=no-member
            max_batch_size=max_batch_size or receive_client._prefetch, timeout=timeout)  # pylint: disable=protected-access, no-member


class _Platform(object):
    """Runs any platform preparatory steps for the AMQP C
    library. This is primarily used for OpenSSL setup.

    :ivar initialized: When the setup has completed.
    :vartype initialized: bool
    """

    initialized = False

    @classmethod
    def initialize(cls):
        """Initialize the TLS/SSL platform to prepare it for
        making AMQP requests. This only needs to happen once.
        """
        if cls.initialized:
            _logger.debug("Platform already initialized.")
        else:
            _logger.debug("Initializing platform.")
            c_uamqp.platform_init()
            cls.initialized = True

    @classmethod
    def deinitialize(cls):
        """Deinitialize the TLS/SSL platform to prepare it for
        making AMQP requests. This only needs to happen once.
        """
        if not cls.initialized:
            _logger.debug("Platform already deinitialized.")
        else:
            #cls.initialized = False
            _logger.debug("Deinitializing platform.")
            #c_uamqp.platform_deinit()


def get_platform_info():
    """Gets the current platform information.

    :rtype: str
    """
    return str(c_uamqp.get_info())
