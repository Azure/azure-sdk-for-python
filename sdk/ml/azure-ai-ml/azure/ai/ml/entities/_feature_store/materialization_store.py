# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._arm_id_utils import AzureResourceId
from azure.ai.ml._utils._experimental import experimental


@experimental
class MaterializationStore:
    def __init__(self, type: str, target: str):  # pylint: disable=redefined-builtin
        """MaterializationStore.
        :param type: store type.
        :type type: str
        :param target: store target.
        :type target: str
        """

        self.type = type
        _ = AzureResourceId(target)
        self.__target = target

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value: str):
        _ = AzureResourceId(value)
        self.__target = value
