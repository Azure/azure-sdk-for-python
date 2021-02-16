# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum


class AutoCollectionType(Enum):
    """Automatic collection of metrics type"""

    PERF_COUNTER = 0
    LIVE_METRICS = 1
