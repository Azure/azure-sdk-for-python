# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.entities._mixins import RestTranslatableMixin


class FeaturizationSettings(RestTranslatableMixin):
    """Base Featurization settings"""

    def __init__(
        self,
        *,
        dataset_language: str = None,
    ):
        self.dataset_language = dataset_language

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FeaturizationSettings):
            return NotImplemented

        return self.dataset_language == other.dataset_language

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
