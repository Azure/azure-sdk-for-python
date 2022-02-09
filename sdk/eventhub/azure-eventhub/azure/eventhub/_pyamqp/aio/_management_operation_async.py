#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import logging
import uuid
import time
from functools import partial

from ._management_link_async import ManagementLink
from ..message import Message
from ..error import (
    AMQPException,
    AMQPConnectionError,
    AMQPLinkError,
    ErrorCondition
)

from ..constants import (
    ManagementOpenResult,
    ManagementExecuteOperationResult
)

_LOGGER = logging.getLogger(__name__)


class ManagementOperation(object):
    def __init__(self, session, endpoint='$management', **kwargs):
        self._mgmt_link_open_status = None

        self._session = session
        self._connection = self._session._connection
        self._mgmt_link = self._session.create_request_response_link_pair(
            endpoint=endpoint,
            on_amqp_management_open_complete=self._on_amqp_management_open_complete,
            on_amqp_management_error=self._on_amqp_management_error,
            **kwargs
        )  # type: ManagementLink
        self._responses = {}
        self._mgmt_error = None

    async def _on_amqp_management_open_complete(self, result):
        """Callback run when the send/receive links are open and ready
        to process messages.

        :param result: Whether the link opening was successful.
        :type result: int
        """
        self._mgmt_link_open_status = result

    async def _on_amqp_management_error(self):
        """Callback run if an error occurs in the send/receive links."""
        # TODO: This probably shouldn't be ValueError
        self._mgmt_error = ValueError("Management Operation error occurred.")

    async def _on_execute_operation_complete(
        self,
        operation_id,
        operation_result,
        status_code,
        status_description,
        raw_message,
        error=None
    ):
        _LOGGER.debug(
            "mgmt operation completed, operation id: %r; operation_result: %r; status_code: %r; "
            "status_description: %r, raw_message: %r, error: %r",
            operation_id,
            operation_result,
            status_code,
            status_description,
            raw_message,
            error
        )

        if operation_result in\
                (ManagementExecuteOperationResult.ERROR, ManagementExecuteOperationResult.LINK_CLOSED):
            self._mgmt_error = error
            _LOGGER.error(
                "Failed to complete mgmt operation due to error: %r. The management request message is: %r",
                error, raw_message
            )
        else:
            self._responses[operation_id] = (status_code, status_description, raw_message)

    async def execute(self, message, operation=None, operation_type=None, timeout=0):
        start_time = time.time()
        operation_id = str(uuid.uuid4())
        self._responses[operation_id] = None
        self._mgmt_error = None

        await self._mgmt_link.execute_operation(
            message,
            partial(self._on_execute_operation_complete, operation_id),
            timeout=timeout,
            operation=operation,
            type=operation_type
        )

        while not self._responses[operation_id] and not self._mgmt_error:
            if timeout > 0:
                now = time.time()
                if (now - start_time) >= timeout:
                    raise TimeoutError("Failed to receive mgmt response in {}ms".format(timeout))
            await self._connection.listen()

        if self._mgmt_error:
            self._responses.pop(operation_id)
            raise self._mgmt_error

        response = self._responses.pop(operation_id)
        return response

    async def open(self):
        self._mgmt_link_open_status = ManagementOpenResult.OPENING
        await self._mgmt_link.open()

    async def ready(self):
        try:
            raise self._mgmt_error
        except TypeError:
            pass

        if self._mgmt_link_open_status == ManagementOpenResult.OPENING:
            return False
        if self._mgmt_link_open_status == ManagementOpenResult.OK:
            return True
        # ManagementOpenResult.ERROR or CANCELLED
        # TODO: update below with correct status code + info
        raise AMQPLinkError(
            condition=ErrorCondition.ClientError,
            description="Failed to open mgmt link, management link status: {}".format(self._mgmt_link_open_status),
            info=None
        )

    async def close(self):
        await self._mgmt_link.close()
