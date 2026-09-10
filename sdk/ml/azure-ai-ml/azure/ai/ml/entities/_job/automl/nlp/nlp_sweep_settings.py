# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.arm_ml_service.models import EarlyTerminationPolicy as RestEarlyTerminationPolicy
from azure.ai.ml._restclient.arm_ml_service.models import SamplingAlgorithmType
from azure.ai.ml.entities._job._input_output_helpers import to_hybrid_rest_model
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.entities._mixins import RestTranslatableMixin


# pylint: disable=protected-access
class NlpSweepSettings(RestTranslatableMixin):
    """Sweep settings for all AutoML NLP tasks.

    :keyword sampling_algorithm: Required. Specifies type of hyperparameter sampling algorithm.
        Possible values include: "Grid", "Random", and "Bayesian".
    :paramtype sampling_algorithm: Union[str, ~azure.ai.ml.automl.SamplingAlgorithmType]
    :keyword early_termination: Early termination policy to end poorly performing training candidates,
        defaults to None.
    :paramtype early_termination: Optional[~azure.mgmt.machinelearningservices.models.EarlyTerminationPolicy]

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

    def _to_rest_object(self) -> Dict[str, Any]:
        # ``NlpSweepSettings`` was dropped from the arm_ml_service (2025-12) model set; emit the
        # camelCase wire dict directly so it round-trips through ``SdkJSONEncoder``.
        rest_obj: Dict[str, Any] = {"samplingAlgorithm": self.sampling_algorithm}
        if self.early_termination is not None:
            # ``early_termination_policy`` is a shared msrest boundary helper; convert its msrest
            # rest object to the arm_ml_service hybrid equivalent so ``SdkJSONEncoder`` can serialize it.
            rest_obj["earlyTermination"] = to_hybrid_rest_model(
                self.early_termination._to_rest_object(), RestEarlyTerminationPolicy
            )
        return rest_obj

    @classmethod
    def _from_rest_object(cls, obj: Dict[str, Any]) -> "NlpSweepSettings":
        early_termination = obj.get("earlyTermination")
        return cls(
            sampling_algorithm=obj.get("samplingAlgorithm"),
            early_termination=(
                EarlyTerminationPolicy._from_rest_object(early_termination) if early_termination else None
            ),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NlpSweepSettings):
            return NotImplemented

        return self.sampling_algorithm == other.sampling_algorithm and self.early_termination == other.early_termination

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
