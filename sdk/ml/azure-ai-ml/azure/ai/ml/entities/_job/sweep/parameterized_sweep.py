# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional, Type, Union

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from ..job_limits import SweepJobLimits
from ..queue_settings import QueueSettings
from .early_termination_policy import (
    BanditPolicy,
    EarlyTerminationPolicy,
    EarlyTerminationPolicyType,
    MedianStoppingPolicy,
    TruncationSelectionPolicy,
)
from .objective import Objective
from .sampling_algorithm import (
    BayesianSamplingAlgorithm,
    GridSamplingAlgorithm,
    RandomSamplingAlgorithm,
    RestBayesianSamplingAlgorithm,
    RestGridSamplingAlgorithm,
    RestRandomSamplingAlgorithm,
    RestSamplingAlgorithm,
    SamplingAlgorithm,
    SamplingAlgorithmType,
)
from .search_space import (
    Choice,
    LogNormal,
    LogUniform,
    Normal,
    QLogNormal,
    QLogUniform,
    QNormal,
    QUniform,
    Randint,
    Uniform,
)

# pylint: disable=unnecessary-lambda
SAMPLING_ALGORITHM_TO_REST_CONSTRUCTOR: Dict[SamplingAlgorithmType, Type[RestSamplingAlgorithm]] = {
    SamplingAlgorithmType.RANDOM: RestRandomSamplingAlgorithm,
    SamplingAlgorithmType.GRID: RestGridSamplingAlgorithm,
    SamplingAlgorithmType.BAYESIAN: RestBayesianSamplingAlgorithm,
}

# pylint: disable=unnecessary-lambda
SAMPLING_ALGORITHM_CONSTRUCTOR: Dict[SamplingAlgorithmType, Type[SamplingAlgorithm]] = {
    SamplingAlgorithmType.RANDOM: RandomSamplingAlgorithm,
    SamplingAlgorithmType.GRID: GridSamplingAlgorithm,
    SamplingAlgorithmType.BAYESIAN: BayesianSamplingAlgorithm,
}


class ParameterizedSweep:
    """Shared logic for standalone and pipeline sweep job."""

    def __init__(
        self,
        limits: Optional[SweepJobLimits] = None,
        sampling_algorithm: Optional[Union[str, SamplingAlgorithm]] = None,
        objective: Optional[Union[Dict, Objective]] = None,
        early_termination: Optional[Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = None,
        search_space: Optional[
            Dict[
                str,
                Union[
                    Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform
                ],
            ]
        ] = None,
        queue_settings: Optional[QueueSettings] = None,
    ) -> None:
        """
        :param limits: Limits for sweep job.
        :type limits: ~azure.ai.ml.sweep.SweepJobLimits
        :param sampling_algorithm: Sampling algorithm for sweep job.
        :type sampling_algorithm: ~azure.ai.ml.sweep.SamplingAlgorithm
        :param objective: Objective for sweep job.
        :type objective: ~azure.ai.ml.sweep.Objective
        :param early_termination: Early termination policy for sweep job.
        :type early_termination: ~azure.ai.ml.entities._job.sweep.early_termination_policy.EarlyTerminationPolicy
        :param search_space: Search space for sweep job.
        :type search_space: Dict[str, Union[~azure.ai.ml.sweep.Choice, ~azure.ai.ml.sweep.LogNormal,
        ~azure.ai.ml.sweep.LogUniform, ~azure.ai.ml.sweep.Normal, ~azure.ai.ml.sweep.QLogNormal,
        ~azure.ai.ml.sweep.QLogUniform, ~azure.ai.ml.sweep.QNormal, ~azure.ai.ml.sweep.QUniform,
        ~azure.ai.ml.sweep.Randint, ~azure.ai.ml.sweep.Uniform]]
        :param queue_settings: Queue settings for sweep job.
        :type queue_settings: ~azure.ai.ml.entities.QueueSettings
        """
        self.sampling_algorithm = sampling_algorithm
        self.early_termination = early_termination
        self._limits = limits
        self.search_space = search_space
        self.queue_settings = queue_settings

        if isinstance(objective, Dict):
            self.objective = Objective(**objective)
        else:
            self.objective = objective

    @property
    def limits(self) -> SweepJobLimits:
        """Limits for sweep job.

        :returns: Limits for sweep job.
        :rtype: ~azure.ai.ml.sweep.SweepJobLimits
        """
        return self._limits

    @limits.setter
    def limits(self, value: SweepJobLimits) -> None:
        """Set limits for sweep job.

        :param value: Limits for sweep job.
        :type value: ~azure.ai.ml.sweep.SweepJobLimits
        """
        if not isinstance(value, SweepJobLimits):
            msg = f"limits must be SweepJobLimits but get {type(value)} instead"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SWEEP_JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        self._limits = value

    def set_limits(
        self,
        *,
        max_concurrent_trials: Optional[int] = None,
        max_total_trials: Optional[int] = None,
        timeout: Optional[int] = None,
        trial_timeout: Optional[int] = None,
    ) -> None:
        """Set limits for Sweep node. Leave parameters as None if you don't want to update corresponding values.

        :keyword max_concurrent_trials: maximum concurrent trial number.
        :paramtype max_concurrent_trials: int
        :keyword max_total_trials: maximum total trial number.
        :paramtype max_total_trials: int
        :keyword timeout: total timeout in seconds for sweep node
        :paramtype timeout: int
        :keyword trial_timeout: timeout in seconds for each trial
        :paramtype trial_timeout: int
        """
        if self._limits is None:
            self._limits = SweepJobLimits(
                max_concurrent_trials=max_concurrent_trials,
                max_total_trials=max_total_trials,
                timeout=timeout,
                trial_timeout=trial_timeout,
            )
        else:
            if max_concurrent_trials is not None:
                self.limits.max_concurrent_trials = max_concurrent_trials
            if max_total_trials is not None:
                self.limits.max_total_trials = max_total_trials
            if timeout is not None:
                self.limits.timeout = timeout
            if trial_timeout is not None:
                self.limits.trial_timeout = trial_timeout

    def set_objective(self, *, goal: Optional[str] = None, primary_metric: Optional[str] = None) -> None:
        """Set the sweep object.. Leave parameters as None if you don't want to update corresponding values.

        :keyword goal: Defines supported metric goals for hyperparameter tuning. Acceptable values are:
        "minimize", "maximize".
        :type goal: str
        :keyword primary_metric: Name of the metric to optimize.
        :paramtype primary_metric: str
        """

        if self.objective is not None:
            if goal:
                self.objective.goal = goal
            if primary_metric:
                self.objective.primary_metric = primary_metric
        else:
            self.objective = Objective(goal=goal, primary_metric=primary_metric)

    @property
    def sampling_algorithm(self) -> Union[str, SamplingAlgorithm]:
        """Sampling algorithm for sweep job.

        :returns: Sampling algorithm for sweep job.
        :rtype: ~azure.ai.ml.sweep.SamplingAlgorithm
        """
        return self._sampling_algorithm

    @sampling_algorithm.setter
    def sampling_algorithm(self, value: Optional[Union[SamplingAlgorithm, str]] = None) -> None:
        """Set sampling algorithm for sweep job.

        :param value: Sampling algorithm for sweep job.
        :type value: ~azure.ai.ml.sweep.SamplingAlgorithm
        """
        if value is None:
            self._sampling_algorithm = None
        elif isinstance(value, SamplingAlgorithm):
            self._sampling_algorithm = value
        elif isinstance(value, str) and value.lower().capitalize() in SAMPLING_ALGORITHM_CONSTRUCTOR:
            self._sampling_algorithm = value
        else:
            msg = f"unsupported sampling algorithm: {value}"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SWEEP_JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    def _get_rest_sampling_algorithm(self) -> RestSamplingAlgorithm:
        # TODO: self.sampling_algorithm will always return SamplingAlgorithm
        if isinstance(self.sampling_algorithm, SamplingAlgorithm):
            return self.sampling_algorithm._to_rest_object()  # pylint: disable=protected-access

        if isinstance(self.sampling_algorithm, str):
            return SAMPLING_ALGORITHM_CONSTRUCTOR[  # pylint: disable=protected-access
                SamplingAlgorithmType(self.sampling_algorithm.lower().capitalize())
            ]()._to_rest_object()

        msg = f"Received unsupported value {self._sampling_algorithm} as the sampling algorithm"
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.SWEEP_JOB,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )

    @property
    def early_termination(self) -> Union[str, EarlyTerminationPolicy]:
        """Early termination policy for sweep job.

        :returns: Early termination policy for sweep job.
        :rtype: ~azure.ai.ml.entities._job.sweep.early_termination_policy.EarlyTerminationPolicy
        """
        return self._early_termination

    @early_termination.setter
    def early_termination(self, value: Union[EarlyTerminationPolicy, str]) -> None:
        """Set early termination policy for sweep job.

        :param value: Early termination policy for sweep job.
        :type value: ~azure.ai.ml.entities._job.sweep.early_termination_policy.EarlyTerminationPolicy
        """
        if value is None:
            self._early_termination = None
        elif isinstance(value, EarlyTerminationPolicy):
            self._early_termination = value
        elif isinstance(value, str):
            value = value.lower().capitalize()
            if value == EarlyTerminationPolicyType.BANDIT:
                self._early_termination = BanditPolicy()
            elif value == EarlyTerminationPolicyType.MEDIAN_STOPPING:
                self._early_termination = MedianStoppingPolicy()
            elif value == EarlyTerminationPolicyType.TRUNCATION_SELECTION:
                self._early_termination = TruncationSelectionPolicy()
            else:
                msg = f"Received unsupported value {value} as the early termination policy"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.SWEEP_JOB,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
        else:
            msg = f"Received unsupported value of type {type(value)} as the early termination policy"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SWEEP_JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
