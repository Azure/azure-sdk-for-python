# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    NlpVerticalFeaturizationSettings as RestNlpVerticalFeaturizationSettings,
)
from azure.ai.ml.entities._job.automl.featurization_settings import FeaturizationSettings


class NlpFeaturizationSettings(FeaturizationSettings):
    """Featurization settings for all AutoML NLP Verticals."""

    def __init__(
        self,
        *,
        dataset_language: str = None,
    ):
        super().__init__(dataset_language=dataset_language)

    def _to_rest_object(self) -> RestNlpVerticalFeaturizationSettings:
        return RestNlpVerticalFeaturizationSettings(
            dataset_language=self.dataset_language,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestNlpVerticalFeaturizationSettings) -> "NlpFeaturizationSettings":
        return cls(
            dataset_language=obj.dataset_language,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NlpFeaturizationSettings):
            return NotImplemented

        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
