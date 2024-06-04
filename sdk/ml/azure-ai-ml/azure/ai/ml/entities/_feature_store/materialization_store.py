# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._arm_id_utils import AzureResourceId


class MaterializationStore:
    """Materialization Store

    :param type: The type of the materialization store.
    :type type: str
    :param target: The ARM ID of the materialization store target.
    :type target: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_featurestore.py
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
    def target(self) -> str:
        """Get target value

        :return: returns the ID of the target
        :rtype: str
        """
        return self.__target

    @target.setter
    def target(self, value: str) -> None:
        """Set target value

        :param value: the ID of the target
        :type value: str
        :raises ~azure.ai.ml.exceptions.ValidationException~: Raised if the value is an invalid ARM ID.
        """
        _ = AzureResourceId(value)
        self.__target = value
