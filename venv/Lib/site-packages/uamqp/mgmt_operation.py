#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import uuid

import six
# from uamqp.session import Session
from uamqp import Message, c_uamqp, compat, constants, errors

_logger = logging.getLogger(__name__)


class MgmtOperation(object):
    """An AMQP request/response operation. These are frequently used
    for management tasks against a $management node, however any node name can be
    specified and the available options will depend on the target service.

    :param session: The AMQP session to use for the operation. Both send and
     receive links will be created in this Session.
    :type session: ~uamqp.session.Session
    :param target: The AMQP node to send the request to.
     The default is `b"$management"`
    :type target: bytes or str
    :param status_code_field: Provide an alternate name for the status code in the
     response body which can vary between services due to the spec still being in draft.
     The default is `b"statusCode"`.
    :type status_code_field: bytes or str
    :param description_fields: Provide an alternate name for the description in the
     response body which can vary between services due to the spec still being in draft.
     The default is `b"statusDescription"`.
    :type description_fields: bytes or str
    :param encoding: The encoding to use for parameters supplied as strings.
     Default is 'UTF-8'
    :type encoding: str
    """

    def __init__(self,
                 session,
                 target=None,
                 debug=False,
                 status_code_field=b'statusCode',
                 description_fields=b'statusDescription',
                 encoding='UTF-8'):
        self._encoding = encoding
        self.connection = session._connection  # pylint: disable=protected-access
        # self.session = Session(
        #     connection,
        #     incoming_window=constants.MAX_FRAME_SIZE_BYTES,
        #     outgoing_window=constants.MAX_FRAME_SIZE_BYTES)
        self.target = self._encode(target or constants.MGMT_TARGET)
        status_code_field = self._encode(status_code_field)
        description_fields = self._encode(description_fields)
        self._responses = {}

        self._counter = c_uamqp.TickCounter()
        self._mgmt_op = c_uamqp.create_management_operation(session._session, self.target)  # pylint: disable=protected-access
        self._mgmt_op.set_response_field_names(status_code_field, description_fields)
        self._mgmt_op.set_trace(debug)
        self.open = None
        try:
            self._mgmt_op.open(self)
        except ValueError:
            self.mgmt_error = errors.AMQPConnectionError(
                "Unable to open management session. "
                "Please confirm URI namespace exists.")
        else:
            self.mgmt_error = None

    def _encode(self, value):
        return value.encode(self._encoding) if isinstance(value, six.text_type) else value

    def _management_open_complete(self, result):
        """Callback run when the send/receive links are open and ready
        to process messages.

        :param result: Whether the link opening was successful.
        :type result: int
        """
        self.open = constants.MgmtOpenStatus(result)

    def _management_operation_error(self):
        """Callback run if an error occurs in the send/receive links."""
        self.mgmt_error = ValueError("Management Operation error ocurred.")

    def execute(self, operation, op_type, message, timeout=0):
        """Execute a request and wait on a response.

        :param operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :type operation: bytes or str
        :param op_type: The type on which to carry out the operation. This will
         be specific to the entities of the service. This value will be added as
         an application property on the message.
        :type op_type: bytes or str
        :param message: The message to send in the management request.
        :type message: ~uamqp.message.Message
        :param timeout: Provide an optional timeout in milliseconds within which a response
         to the management request must be received.
        :type timeout: float
        :rtype: ~uamqp.message.Message
        """
        start_time = self._counter.get_current_ms()
        operation_id = str(uuid.uuid4())
        self._responses[operation_id] = None
        operation = self._encode(operation)
        op_type = self._encode(op_type)

        def on_complete(operation_result, status_code, description, wrapped_message):
            result = constants.MgmtExecuteResult(operation_result)
            if result != constants.MgmtExecuteResult.Ok:
                _logger.error(
                    "Failed to complete mgmt operation.\nStatus code: %r\nMessage: %r",
                    status_code, description)
            message = Message(message=wrapped_message) if wrapped_message else None
            self._responses[operation_id] = (status_code, message, description)

        self._mgmt_op.execute(operation, op_type, None, message.get_message(), on_complete)
        while not self._responses[operation_id] and not self.mgmt_error:
            if timeout > 0:
                now = self._counter.get_current_ms()
                if (now - start_time) >= timeout:
                    raise compat.TimeoutException("Failed to receive mgmt response in {}ms".format(timeout))
            self.connection.work()
        if self.mgmt_error:
            raise self.mgmt_error
        response = self._responses.pop(operation_id)
        return response

    def destroy(self):
        """Close the send/receive links for this node."""
        self._mgmt_op.destroy()
