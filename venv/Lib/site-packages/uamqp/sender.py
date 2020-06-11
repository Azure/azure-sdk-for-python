#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import uuid

import six
from uamqp import c_uamqp, constants, errors, utils

_logger = logging.getLogger(__name__)


class MessageSender(object):
    """A Message Sender that opens its own exclsuive Link on an
    existing Session.

    :ivar send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully send. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :vartype send_settle_mode: ~uamqp.constants.SenderSettleMode
    :ivar receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :vartype receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :ivar max_message_size: The maximum allowed message size negotiated for the Link.
    :vartype max_message_size: int

    :param session: The underlying Session with which to send.
    :type session: ~uamqp.session.Session
    :param source: The name of source (i.e. the client).
    :type source: str or bytes
    :param target: The AMQP endpoint to send to.
    :type target: ~uamqp.address.Target
    :param name: A unique name for the sender. If not specified a GUID will be used.
    :type name: str or bytes
    :param send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :type send_settle_mode: ~uamqp.constants.SenderSettleMode
    :param receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :type receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :param max_message_size: The maximum allowed message size negotiated for the Link.
    :type max_message_size: int
    :param link_credit: The sender Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
    :type link_credit: int
    :param properties: Metadata to be sent in the Link ATTACH frame.
    :type properties: dict
    :param error_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :type error_policy: ~uamqp.errors.ErrorPolicy
    :param debug: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :type debug: bool
    :param encoding: The encoding to use for parameters supplied as strings.
     Default is 'UTF-8'
    :type encoding: str
    """

    def __init__(self, session, source, target,
                 name=None,
                 send_settle_mode=constants.SenderSettleMode.Unsettled,
                 receive_settle_mode=constants.ReceiverSettleMode.PeekLock,
                 max_message_size=constants.MAX_MESSAGE_LENGTH_BYTES,
                 link_credit=None,
                 properties=None,
                 error_policy=None,
                 debug=False,
                 encoding='UTF-8'):
        # pylint: disable=protected-access
        if name:
            self.name = name.encode(encoding) if isinstance(name, six.text_type) else name
        else:
            self.name = str(uuid.uuid4()).encode(encoding)
        source = source.encode(encoding) if isinstance(source, six.text_type) else source
        role = constants.Role.Sender

        self.source = c_uamqp.Messaging.create_source(source)
        self.target = target._address.value
        self.error_policy = error_policy or errors.ErrorPolicy()
        self._conn = session._conn
        self._session = session
        self._link = c_uamqp.create_link(session._session, self.name, role.value, self.source, self.target)
        self._link.max_message_size = max_message_size
        self._link.subscribe_to_detach_event(self)

        if link_credit:
            self._link.set_prefetch_count(link_credit)
        if properties:
            self._link.set_attach_properties(utils.data_factory(properties, encoding=encoding))
        if send_settle_mode:
            self.send_settle_mode = send_settle_mode
        if receive_settle_mode:
            self.receive_settle_mode = receive_settle_mode
        if max_message_size:
            self.max_message_size = max_message_size

        self._sender = c_uamqp.create_message_sender(self._link, self)
        self._sender.set_trace(debug)
        self._state = constants.MessageSenderState.Idle
        self._error = None

    def __enter__(self):
        """Open the MessageSender in a context manager."""
        self.open()
        return self

    def __exit__(self, *args):
        """Close the MessageSender when exiting a context manager."""
        self.destroy()

    def _detach_received(self, error):
        """Callback called when a link DETACH frame is received.
        This callback will process the received DETACH error to determine if
        the link is recoverable or whether it should be shutdown.

        :param error: The error information from the detach
         frame.
        :type error: ~uamqp.errors.ErrorResponse
        """
        # pylint: disable=protected-access
        if error:
            condition = error.condition
            description = error.description
            info = error.info
        else:
            condition = b"amqp:unknown-error"
            description = None
            info = None
        self._error = errors._process_link_error(self.error_policy, condition, description, info)
        _logger.info("Received Link detach event: %r\nLink: %r\nDescription: %r"
                     "\nDetails: %r\nRetryable: %r\nConnection: %r",
                     condition, self.name, description, info, self._error.action.retry,
                     self._session._connection.container_id)

    def _state_changed(self, previous_state, new_state):
        """Callback called whenever the underlying Sender undergoes a change
        of state. This function wraps the states as Enums to prepare for
        calling the public callback.

        :param previous_state: The previous Sender state.
        :type previous_state: int
        :param new_state: The new Sender state.
        :type new_state: int
        """
        try:
            try:
                _previous_state = constants.MessageSenderState(previous_state)
            except ValueError:
                _previous_state = previous_state
            try:
                _new_state = constants.MessageSenderState(new_state)
            except ValueError:
                _new_state = new_state
            if _previous_state == constants.MessageSenderState.Opening \
                    and _new_state == constants.MessageSenderState.Error:
                _logger.info("Sender link failed to open - expecting to receive DETACH frame.")
            elif self._session._link_error:  # pylint: disable=protected-access
                _logger.info("Sender link ATTACH frame invalid - expecting to receive DETACH frame.")
            else:
                self.on_state_changed(_previous_state, _new_state)
        except KeyboardInterrupt:
            _logger.error("Received shutdown signal while updating sender state from {} to {}".format(
                previous_state, new_state))
            self._error = errors.AMQPClientShutdown()

    def get_state(self):
        """Get the state of the MessageSender and its underlying Link.

        :rtype: ~uamqp.constants.MessageSenderState
        """
        try:
            raise self._error
        except TypeError:
            pass
        except Exception as e:
            _logger.warning("%r", e)
            raise
        return self._state

    def work(self):
        """Update the link status."""
        self._link.do_work()

    def destroy(self):
        """Close both the Sender and the Link. Clean up any C objects."""
        self._sender.destroy()
        self._link.destroy()

    def open(self):
        """Open the MessageSender in order to start processing messages.

        :raises: ~uamqp.errors.AMQPConnectionError if the Sender raises
         an error on opening. This can happen if the target URI is invalid
         or the credentials are rejected.
        """
        try:
            self._sender.open()
        except ValueError:
            raise errors.AMQPConnectionError(
                "Failed to open Message Sender. "
                "Please confirm credentials and target URI.")

    def close(self):
        """Close the sender, leaving the link intact."""
        self._sender.close()

    def send(self, message, callback, timeout=0):
        """Add a single message to the internal pending queue to be processed
        by the Connection without waiting for it to be sent.

        :param message: The message to send.
        :type message: ~uamqp.message.Message
        :param callback: The callback to be run once a disposition is received
         in receipt of the message. The callback must take three arguments, the message,
         the send result and the optional delivery condition (exception).
        :type callback:
         callable[~uamqp.message.Message, ~uamqp.constants.MessageSendResult, ~uamqp.errors.MessageException]
        :param timeout: An expiry time for the message added to the queue. If the
         message is not sent within this timeout it will be discarded with an error
         state. If set to 0, the message will not expire. The default is 0.
        """
        # pylint: disable=protected-access
        try:
            raise self._error
        except TypeError:
            pass
        except Exception as e:
            _logger.warning("%r", e)
            raise
        c_message = message.get_message()
        message._on_message_sent = callback
        try:
            self._session._connection.lock(timeout=-1)
            return self._sender.send(c_message, timeout, message)
        finally:
            self._session._connection.release()

    def on_state_changed(self, previous_state, new_state):
        """Callback called whenever the underlying Sender undergoes a change
        of state. This function can be overridden.

        :param previous_state: The previous Sender state.
        :type previous_state: ~uamqp.constants.MessageSenderState
        :param new_state: The new Sender state.
        :type new_state: ~uamqp.constants.MessageSenderState
        """
        # pylint: disable=protected-access
        _logger.info("Message sender %r state changed from %r to %r on connection: %r",
                     self.name, previous_state, new_state, self._session._connection.container_id)
        self._state = new_state

    @property
    def send_settle_mode(self):
        return self._link.send_settle_mode

    @send_settle_mode.setter
    def send_settle_mode(self, value):
        self._link.send_settle_mode = value.value

    @property
    def receive_settle_mode(self):
        return self._link.receive_settle_mode

    @receive_settle_mode.setter
    def receive_settle_mode(self, value):
        self._link.receive_settle_mode = value.value

    @property
    def max_message_size(self):
        return self._link.max_message_size

    @max_message_size.setter
    def max_message_size(self, value):
        self._link.max_message_size = int(value)
