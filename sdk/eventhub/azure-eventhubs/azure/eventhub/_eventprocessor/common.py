# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from enum import Enum


class CloseReason(Enum):
    """
    A partition consumer is closed due to two reasons:
    SHUTDOWN: It is explicitly required to stop, this would happen when the EventHubConsumerClient is closed.
    OWNERSHIP_LOST: It loses the ownership of a partition, this would happend when other EventHubConsumerClient
    instance claims ownership of the partition.
    """
    SHUTDOWN = 0
    OWNERSHIP_LOST = 1


class OwnershipLostError(Exception):
    """Raises when update_checkpoint detects the ownership to a partition has been lost.

    """
