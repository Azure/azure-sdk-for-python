#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import functools
import logging
import uuid

import six
import uamqp
from uamqp import c_uamqp, constants, errors, utils

_logger = logging.getLogger(__name__)


class MessageReceiver(object):
    """A Message Receiver that opens its own exclsuive Link on an
    existing Session.

    :ivar receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :vartype receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :ivar send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :vartype send_settle_mode: ~uamqp.constants.SenderSettleMode
    :ivar max_message_size: The maximum allowed message size negotiated for the Link.
    :vartype max_message_size: int

    :param session: The underlying Session with which to receive.
    :type session: ~uamqp.session.Session
    :param source: The AMQP endpoint to receive from.
    :type source: ~uamqp.address.Source
    :param target: The name of target (i.e. the client).
    :type target: str or bytes
    :param name: A unique name for the receiver. If not specified a GUID will be used.
    :type name: str or bytes
    :param receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :type receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :param send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :type send_settle_mode: ~uamqp.constants.SenderSettleMode
    :param desired_capabilities: The extension capabilities desired from the peer endpoint.
     To create an desired_capabilities object, please do as follows:
        - 1. Create an array of desired capability symbols: `capabilities_symbol_array = [types.AMQPSymbol(string)]`
        - 2. Transform the array to AMQPValue object: `utils.data_factory(types.AMQPArray(capabilities_symbol_array))`
    :type desired_capabilities: ~uamqp.c_uamqp.AMQPValue
    :param max_message_size: The maximum allowed message size negotiated for the Link.
    :type max_message_size: int
    :param prefetch: The receiver Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
    :type prefetch: int
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
                 on_message_received,
                 name=None,
                 receive_settle_mode=constants.ReceiverSettleMode.PeekLock,
                 send_settle_mode=constants.SenderSettleMode.Unsettled,
                 max_message_size=constants.MAX_MESSAGE_LENGTH_BYTES,
                 prefetch=300,
                 properties=None,
                 error_policy=None,
                 debug=False,
                 encoding='UTF-8',
                 desired_capabilities=None):
        # pylint: disable=protected-access
        if name:
            self.name = name.encode(encoding) if isinstance(name, six.text_type) else name
        else:
            self.name = str(uuid.uuid4()).encode(encoding)
        target = target.encode(encoding) if isinstance(target, six.text_type) else target
        role = constants.Role.Receiver

        self.source = source._address.value
        self.target = c_uamqp.Messaging.create_target(target)
        self.on_message_received = on_message_received
        self.encoding = encoding
        self.error_policy = error_policy or errors.ErrorPolicy()
        self._settle_mode = receive_settle_mode
        self._conn = session._conn
        self._session = session
        self._link = c_uamqp.create_link(session._session, self.name, role.value, self.source, self.target)
        self._link.subscribe_to_detach_event(self)
        if prefetch:
            self._link.set_prefetch_count(prefetch)
        if properties:
            self._link.set_attach_properties(utils.data_factory(properties, encoding=encoding))
        if receive_settle_mode:
            self.receive_settle_mode = receive_settle_mode
        if send_settle_mode:
            self.send_settle_mode = send_settle_mode
        if max_message_size:
            self.max_message_size = max_message_size
        if desired_capabilities:
            self._link.set_desired_capabilities(desired_capabilities)

        self._receiver = c_uamqp.create_message_receiver(self._link, self)
        self._receiver.set_trace(debug)
        self._state = constants.MessageReceiverState.Idle
        self._error = None

    def __enter__(self):
        """Open the MessageReceiver in a context manager."""
        self.open()
        return self

    def __exit__(self, *args):
        """Close the MessageReceiver when exiting a context manager."""
        self.destroy()

    def _state_changed(self, previous_state, new_state):
        """Callback called whenever the underlying Receiver undergoes a change
        of state. This function wraps the states as Enums to prepare for
        calling the public callback.

        :param previous_state: The previous Receiver state.
        :type previous_state: int
        :param new_state: The new Receiver state.
        :type new_state: int
        """
        try:
            try:
                _previous_state = constants.MessageReceiverState(previous_state)
            except ValueError:
                _previous_state = previous_state
            try:
                _new_state = constants.MessageReceiverState(new_state)
            except ValueError:
                _new_state = new_state
            if _previous_state == constants.MessageReceiverState.Opening \
                    and _new_state == constants.MessageReceiverState.Error:
                _logger.info("Receiver link failed to open - expecting to receive DETACH frame.")
            elif self._session._link_error:  # pylint: disable=protected-access
                _logger.info("Receiver link ATTACH frame invalid - expecting to receive DETACH frame.")
            else:
                self.on_state_changed(_previous_state, _new_state)
        except KeyboardInterrupt:
            _logger.error("Received shutdown signal while updating receiver state from {} to {}".format(
                previous_state, new_state))
            self._error = errors.AMQPClientShutdown()

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

    def _settle_message(self, message_number, response):
        """Send a settle dispostition for a received message.

        :param message_number: The delivery number of the message
         to settle.
        :type message_number: int
        :response: The type of disposition to respond with, e.g. whether
         the message was accepted, rejected or abandoned.
        :type response: ~uamqp.errors.MessageResponse
        """
        if not response or isinstance(response, errors.MessageAlreadySettled):
            return
        if isinstance(response, errors.MessageAccepted):
            self._receiver.settle_accepted_message(message_number)
        elif isinstance(response, errors.MessageReleased):
            self._receiver.settle_released_message(message_number)
        elif isinstance(response, errors.MessageRejected):
            self._receiver.settle_rejected_message(
                message_number,
                response.error_condition,
                response.error_description,
                response.error_info)
        elif isinstance(response, errors.MessageModified):
            self._receiver.settle_modified_message(
                message_number,
                response.failed,
                response.undeliverable,
                response.annotations)
        else:
            raise ValueError("Invalid message response type: {}".format(response))

    def _message_received(self, message):
        """Callback run on receipt of every message. If there is
        a user-defined callback, this will be called.
        Additionally if the client is retrieving messages for a batch
        or iterator, the message will be added to an internal queue.

        :param message: c_uamqp.Message
        """
        # pylint: disable=protected-access
        message_number = self._receiver.last_received_message_number()
        if self._settle_mode == constants.ReceiverSettleMode.ReceiveAndDelete:
            settler = None
        else:
            settler = functools.partial(self._settle_message, message_number)
        try:
            wrapped_message = uamqp.Message(
                message=message,
                encoding=self.encoding,
                settler=settler,
                delivery_no=message_number)
            self.on_message_received(wrapped_message)
        except RuntimeError:
            condition = b"amqp:unknown-error"
            self._error = errors._process_link_error(self.error_policy, condition, None, None)
            _logger.info("Unable to settle message no %r. Disconnecting.\nLink: %r\nConnection: %r",
                         message_number,
                         self.name,
                         self._session._connection.container_id)
        except KeyboardInterrupt:
            _logger.error("Received shutdown signal while processing message no %r\nRejecting message.", message_number)
            self._receiver.settle_modified_message(message_number, True, True, None)
            self._error = errors.AMQPClientShutdown()
        except Exception as e:  # pylint: disable=broad-except
            _logger.error("Error processing message no %r: %r\nRejecting message.", message_number, e)
            self._receiver.settle_modified_message(message_number, True, True, None)

    def get_state(self):
        """Get the state of the MessageReceiver and its underlying Link.

        :rtype: ~uamqp.constants.MessageReceiverState
        """
        try:
            raise self._error
        except TypeError:
            pass
        except errors.LinkRedirect as e:
            _logger.info("%r", e)
            raise
        except Exception as e:
            _logger.warning("%r", e)
            raise
        return self._state

    def work(self):
        """Update the link status."""
        self._link.do_work()

    def destroy(self):
        """Close both the Receiver and the Link. Clean up any C objects."""
        self._receiver.destroy()
        self._link.destroy()

    def open(self):
        """Open the MessageReceiver in order to start processing messages.

        :raises: ~uamqp.errors.AMQPConnectionError if the Receiver raises
         an error on opening. This can happen if the source URI is invalid
         or the credentials are rejected.
        """
        try:
            self._receiver.open(self)
        except ValueError:
            raise errors.AMQPConnectionError(
                "Failed to open Message Receiver. "
                "Please confirm credentials and target URI.")

    def close(self):
        """Close the Receiver, leaving the link intact."""
        self._receiver.close()

    def on_state_changed(self, previous_state, new_state):
        """Callback called whenever the underlying Receiver undergoes a change
        of state. This function can be overridden.

        :param previous_state: The previous Receiver state.
        :type previous_state: ~uamqp.constants.MessageReceiverState
        :param new_state: The new Receiver state.
        :type new_state: ~uamqp.constants.MessageReceiverState
        """
        # pylint: disable=protected-access
        _logger.info("Message receiver %r state changed from %r to %r on connection: %r",
                     self.name, previous_state, new_state, self._session._connection.container_id)
        self._state = new_state

    @property
    def receive_settle_mode(self):
        return self._link.receive_settle_mode

    @receive_settle_mode.setter
    def receive_settle_mode(self, value):
        self._link.receive_settle_mode = value.value

    @property
    def send_settle_mode(self):
        return self._link.send_settle_mode

    @send_settle_mode.setter
    def send_settle_mode(self, value):
        self._link.send_settle_mode = value.value

    @property
    def max_message_size(self):
        return self._link.max_message_size

    @max_message_size.setter
    def max_message_size(self, value):
        self._link.max_message_size = int(value)
