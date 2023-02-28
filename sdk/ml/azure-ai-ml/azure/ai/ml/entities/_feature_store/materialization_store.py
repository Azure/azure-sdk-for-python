# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class MaterializationStore:
    def __init__(self, type: str, target: str):  # pylint: disable=redefined-builtin
        self.type = type
        self.target = target
