#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging

from uamqp import constants, errors, session
from uamqp.utils import get_running_loop
from uamqp.async_ops.mgmt_operation_async import MgmtOperationAsync

_logger = logging.getLogger(__name__)


class SessionAsync(session.Session):
    """An asynchronous AMQP Session. A Connection can have multiple Sessions, and each
    Session can have multiple Links.
    An async Session must be used with an async Connection.

    :ivar incoming_window: The size of the allowed window for incoming messages.
    :vartype incoming_window: int
    :ivar outgoing_window: The size of the allowed window for outgoing messages.
    :vartype outgoing_window: int
    :ivar handle_max: The maximum number of concurrent link handles.
    :vartype handle_max: int

    :param connection: The underlying Connection for the Session.
    :type connection: ~uamqp.async_ops.connection_async.ConnectionAsync
    :param incoming_window: The size of the allowed window for incoming messages.
    :type incoming_window: int
    :param outgoing_window: The size of the allowed window for outgoing messages.
    :type outgoing_window: int
    :param handle_max: The maximum number of concurrent link handles.
    :type handle_max: int
    :param on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :type on_attach: func[~uamqp.address.Source, ~uamqp.address.Target, dict, ~uamqp.errors.AMQPConnectionError]
    :param loop: A user specified event loop.
    :type loop: ~asycnio.AbstractEventLoop
    """

    def __init__(self, connection,
                 incoming_window=None,
                 outgoing_window=None,
                 handle_max=None,
                 on_attach=None,
                 loop=None):
        self.loop = loop or get_running_loop()
        super(SessionAsync, self).__init__(
            connection,
            incoming_window=incoming_window,
            outgoing_window=outgoing_window,
            handle_max=handle_max,
            on_attach=on_attach)

    async def __aenter__(self):
        """Run Session in an async context manager."""
        return self

    async def __aexit__(self, *args):
        """Close and destroy sesion on exiting  an async context manager."""
        await self.destroy_async()

    async def mgmt_request_async(self, message, operation, op_type=None, node=b'$management', **kwargs):
        """Asynchronously run a request/response operation. These are frequently used
        for management tasks against a $management node, however any node name can be
        specified and the available options will depend on the target service.

        :param message: The message to send in the management request.
        :type message: ~uamqp.message.Message
        :param operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :type operation: bytes or str
        :param op_type: The type on which to carry out the operation. This will
         be specific to the entities of the service. This value will be added as
         an application property on the message.
        :type op_type: bytes or str
        :param node: The target node. Default is `b"$management"`.
        :type node: bytes or str
        :param timeout: Provide an optional timeout in milliseconds within which a response
         to the management request must be received.
        :type timeout: float
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
        :rtype: ~uamqp.message.Message
        """
        timeout = kwargs.pop('timeout', None) or 0
        parse_response = kwargs.pop('callback', None)
        try:
            mgmt_link = self._mgmt_links[node]
        except KeyError:
            mgmt_link = MgmtOperationAsync(self, target=node, loop=self.loop, **kwargs)
            self._mgmt_links[node] = mgmt_link
            while not mgmt_link.open and not mgmt_link.mgmt_error:
                await self._connection.work_async()
            if mgmt_link.mgmt_error:
                raise mgmt_link.mgmt_error
            if mgmt_link.open != constants.MgmtOpenStatus.Ok:
                raise errors.AMQPConnectionError("Failed to open mgmt link: {}".format(mgmt_link.open))
        op_type = op_type or b'empty'
        status, response, description = await mgmt_link.execute_async(operation, op_type, message, timeout=timeout)
        if parse_response:
            return parse_response(status, response, description)
        return response

    async def destroy_async(self):
        """Asynchronously close any open management Links and close the Session.
        Cleans up and C objects for both mgmt Links and Session.
        """
        for _, link in self._mgmt_links.items():
            await link.destroy_async()
        self._session.destroy()
