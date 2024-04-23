# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import NlpSweepSettings as RestNlpSweepSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import SamplingAlgorithmType
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.entities._mixins import RestTranslatableMixin


# pylint: disable=protected-access
class NlpSweepSettings(RestTranslatableMixin):
    """Sweep settings for all AutoML NLP tasks.

    :param sampling_algorithm: Required. Specifies type of hyperparameter sampling algorithm.
        Possible values include: "Grid", "Random", and "Bayesian".
    :type sampling_algorithm: Union[str, ~azure.ai.ml.automl.SamplingAlgorithmType]
    :param early_termination: Early termination policy to end poorly performing training candidates,
        defaults to None.
    :type early_termination: Optional[~azure.mgmt.machinelearningservices.models.EarlyTerminationPolicy]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.nlp_sweep_settings]
                :end-before: [END automl.nlp_sweep_settings]
                :language: python
                :dedent: 8
                :caption: creating an nlp sweep settings
    """

    def __init__(
        self,
        *,
        sampling_algorithm: Union[str, SamplingAlgorithmType],
        early_termination: Optional[EarlyTerminationPolicy] = None,
    ):
        self.sampling_algorithm = sampling_algorithm
        self.early_termination = early_termination

    def _to_rest_object(self) -> RestNlpSweepSettings:
        return RestNlpSweepSettings(
            sampling_algorithm=self.sampling_algorithm,
            early_termination=self.early_termination._to_rest_object() if self.early_termination else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestNlpSweepSettings) -> "NlpSweepSettings":
        return cls(
            sampling_algorithm=obj.sampling_algorithm,
            early_termination=(
                EarlyTerminationPolicy._from_rest_object(obj.early_termination) if obj.early_termination else None
            ),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NlpSweepSettings):
            return NotImplemented

        return self.sampling_algorithm == other.sampling_algorithm and self.early_termination == other.early_termination

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
