# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._experimental import experimental


@experimental
class _MaterializationStore:
    def __init__(self, type: str, target: str):  # pylint: disable=redefined-builtin

        """_MaterializationStore.
        :param type: store type.
        :type type: str
        :param target: store target.
        :type target: str
        """

        self.type = type
        self.target = target
