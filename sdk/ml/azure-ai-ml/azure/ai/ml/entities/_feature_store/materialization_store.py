# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._experimental import experimental


@experimental
class MaterializationStore:
    def __init__(self, type: str, target: str):  # pylint: disable=redefined-builtin
        self.type = type
        self.target = target
