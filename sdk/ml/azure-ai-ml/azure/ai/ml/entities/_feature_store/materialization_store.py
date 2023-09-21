# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._arm_id_utils import AzureResourceId
from azure.ai.ml._utils._experimental import experimental


@experimental
class MaterializationStore:
    """Materialization Store

    :param type: The type of the materialization store.
    :type type: str
    :param target: The Azure Resource ID of the materialization store target.
    :type target: str

    .. admonition:: Example:

        .. literalinclude:: ../../../../../../samples/ml_samples_featurestore.py
            :start-after: [START configure_materialization_store]
            :end-before: [END configure_materialization_store]
            :language: Python
            :dedent: 8
            :caption: Configuring a Materialization Store
    """
    def __init__(self, type: str, target: str) -> None:  # pylint: disable=redefined-builtin
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
