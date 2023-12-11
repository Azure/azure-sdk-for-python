# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class DataAvailabilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """DataAvailabilityStatus."""

    NONE = "None"
    PENDING = "Pending"
    INCOMPLETE = "Incomplete"
    COMPLETE = "Complete"
