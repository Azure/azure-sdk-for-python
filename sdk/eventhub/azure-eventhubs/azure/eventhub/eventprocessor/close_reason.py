# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from enum import Enum


class CloseReason(Enum):
    SHUTDOWN = 0  # user call EventProcessor.stop()
    LEASE_LOST = 1  # lose the ownership of a partition.
    EVENTHUB_EXCEPTION = 2  # Exception happens during receiving events
    USER_EXCEPTION = 3  # user's code in EventProcessor.process_events() raises an exception
