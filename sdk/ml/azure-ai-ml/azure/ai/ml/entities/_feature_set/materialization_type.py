# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta
from azure.ai.ml._utils._experimental import experimental


@experimental
class MaterializationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    RECURRENT_MATERIALIZATION = 1
    BACKFILL_MATERIALIZATION = 2
