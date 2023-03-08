# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.ai.ml._utils._experimental import experimental


@experimental
class MaterializationType(Enum):
    RecurrentMaterialization = 1
    BackfillMaterialization = 2
