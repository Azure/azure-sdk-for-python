#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging

from uamqp import c_uamqp, constants, errors, mgmt_operation
from uamqp.address import Source, Target

_logger = logging.getLogger(__name__)


class Session(object):
    """An AMQP Session. A Connection can have multiple Sessions, and each
    Session can have multiple Links.

    :ivar incoming_window: The size of the allowed window for incoming messages.
    :vartype incoming_window: int
    :ivar outgoing_window: The size of the allowed window for outgoing messages.
    :vartype outgoing_window: int
    :ivar handle_max: The maximum number of concurrent link handles.
    :vartype handle_max: int

    :param connection: The underlying Connection for the Session.
    :type connection: ~uamqp.connection.Connection
    :param incoming_window: The size of the allowed window for incoming messages.
    :type incoming_window: int
    :param outgoing_window: The size of the allowed window for outgoing messages.
    :type outgoing_window: int
    :param handle_max: The maximum number of concurrent link handles.
    :type handle_max: int
    :param on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :type on_attach: func[~uamqp.address.Source, ~uamqp.address.Target, dict, ~uamqp.errors.AMQPConnectionError]
    """

    def __init__(self, connection,
                 incoming_window=None,
                 outgoing_window=None,
                 handle_max=None,
                 on_attach=None):
        self._connection = connection
        self._conn = connection._conn  # pylint: disable=protected-access
        self._session = c_uamqp.create_session(self._conn, self)
        self._mgmt_links = {}
        self._link_error = None
        self._on_attach = on_attach

        if incoming_window:
            self.incoming_window = incoming_window
        if outgoing_window:
            self.outgoing_window = outgoing_window
        if handle_max:
            self.handle_max = handle_max

    def __enter__(self):
        """Run Session in a context manager."""
        return self

    def __exit__(self, *args):
        """Close and destroy sesion on exiting context manager."""
        self._session.destroy()

    def _attach_received(self, source, target, properties, error=None):
        if error:
            self._link_error = errors.AMQPConnectionError(error)
        if self._on_attach:
            if source and target:
                source = Source.from_c_obj(source)
                target = Target.from_c_obj(target)
            if properties:
                properties = properties.value
            self._on_attach(source, target, properties, self._link_error)

    def mgmt_request(self, message, operation, op_type=None, node=b'$management', **kwargs):
        """Run a request/response operation. These are frequently used for management
        tasks against a $management node, however any node name can be specified
        and the available options will depend on the target service.

        :param message: The message to send in the management request.
        :type message: ~uamqp.message.Message
        :param operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :type operation: bytes
        :param op_type: The type on which to carry out the operation. This will
         be specific to the entities of the service. This value will be added as
         an application property on the message.
        :type op_type: bytes
        :param node: The target node. Default is `b"$management"`.
        :type node: bytes
        :param timeout: Provide an optional timeout in milliseconds within which a response
         to the management request must be received.
        :type timeout: float
        :param status_code_field: Provide an alternate name for the status code in the
         response body which can vary between services due to the spec still being in draft.
         The default is `b"statusCode"`.
        :type status_code_field: bytes
        :param description_fields: Provide an alternate name for the description in the
         response body which can vary between services due to the spec still being in draft.
         The default is `b"statusDescription"`.
        :type description_fields: bytes
        :param encoding: The encoding to use for parameters supplied as strings.
         Default is 'UTF-8'
        :type encoding: str
        :rtype: ~uamqp.message.Message
        """
        timeout = kwargs.pop('timeout', None) or 0
        parse_response = kwargs.pop('callback', None)
        try:
            mgmt_link = self._mgmt_links[node]
        except KeyError:
            mgmt_link = mgmt_operation.MgmtOperation(self, target=node, **kwargs)
            self._mgmt_links[node] = mgmt_link
            while not mgmt_link.open and not mgmt_link.mgmt_error:
                self._connection.work()
            if mgmt_link.mgmt_error:
                raise mgmt_link.mgmt_error
            if mgmt_link.open != constants.MgmtOpenStatus.Ok:
                raise errors.AMQPConnectionError("Failed to open mgmt link: {}".format(mgmt_link.open))
        op_type = op_type or b'empty'
        status, response, description = mgmt_link.execute(operation, op_type, message, timeout=timeout)
        if parse_response:
            return parse_response(status, response, description)
        return response

    def destroy(self):
        """Close any open management Links and close the Session.
        Cleans up and C objects for both mgmt Links and Session.
        """
        for _, link in self._mgmt_links.items():
            link.destroy()
        self._session.destroy()

    @property
    def incoming_window(self):
        return self._session.incoming_window

    @incoming_window.setter
    def incoming_window(self, value):
        self._session.incoming_window = int(value)

    @property
    def outgoing_window(self):
        return self._session.outgoing_window

    @outgoing_window.setter
    def outgoing_window(self, value):
        self._session.outgoing_window = int(value)

    @property
    def handle_max(self):
        return self._session.handle_max

    @handle_max.setter
    def handle_max(self, value):
        self._session.handle_max = int(value)
