# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    NlpVerticalFeaturizationSettings as RestNlpVerticalFeaturizationSettings,
)
from azure.ai.ml.entities._job.automl.featurization_settings import FeaturizationSettings, FeaturizationSettingsType


class NlpFeaturizationSettings(FeaturizationSettings):
    """Featurization settings for all AutoML NLP Verticals.

    :ivar type: Specifies the type of FeaturizationSettings. Set automatically to "NLP" for this class.
    :vartype type: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.nlp_featurization_settings]
                :end-before: [END automl.nlp_featurization_settings]
                :language: python
                :dedent: 8
                :caption: creating an nlp featurization settings
    """

    type = FeaturizationSettingsType.NLP

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
