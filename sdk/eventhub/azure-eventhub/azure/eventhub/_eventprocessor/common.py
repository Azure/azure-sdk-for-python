# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum


class CloseReason(Enum):
    """The reason a partition consumer is closed."""

    # The Consumer was explicitly required to stop. This would happen when the EventHubConsumerClient is closed.
    SHUTDOWN = 0

    # The Consumer lost the ownership of a partition. This would happend when another EventHubConsumerClient
    # instance claims ownership of the partition.
    OWNERSHIP_LOST = 1


class LoadBalancingStrategy(Enum):
    GREEDY = "greedy"
    BALANCED = "balanced"
