# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class MaterializationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Materialization Type Enum"""

    RECURRENT_MATERIALIZATION = 1
    BACKFILL_MATERIALIZATION = 2
