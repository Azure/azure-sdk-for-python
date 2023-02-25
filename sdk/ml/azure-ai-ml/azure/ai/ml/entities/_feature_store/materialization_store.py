# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class MaterializationStore:
    def __init__(
        self,
        type: str,
        target: str
    ):
        self.type = type
        self.target = target
