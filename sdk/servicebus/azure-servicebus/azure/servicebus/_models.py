# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------


class DeleteMessagesResult:
    """The result of a batch delete operation.

    :ivar int deleted_message_count: The number of messages deleted by the service.
    """

    def __init__(self, deleted_message_count: int) -> None:
        self._deleted_message_count = deleted_message_count

    @property
    def deleted_message_count(self) -> int:
        """The number of messages deleted by the service.

        :rtype: int
        """
        return self._deleted_message_count


class PurgeMessagesResult(DeleteMessagesResult):
    """The result of a purge operation.

    :ivar int deleted_message_count: The total number of messages deleted by the service.
    """
