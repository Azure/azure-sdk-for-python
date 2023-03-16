# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional, Type, Union

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from ..job_limits import SweepJobLimits
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
    ):
        self.sampling_algorithm = sampling_algorithm
        self.early_termination = early_termination
        self._limits = limits
        self.search_space = search_space

        if isinstance(objective, Dict):
            self.objective = Objective(**objective)
        else:
            self.objective = objective

    @property
    def limits(self):
        return self._limits

    @limits.setter
    def limits(self, value: SweepJobLimits):
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

        :param max_concurrent_trials: maximum concurrent trial number.
        :type max_concurrent_trials: int
        :param max_total_trials: maximum total trial number.
        :type max_total_trials: int
        :param timeout: total timeout in seconds for sweep node
        :type timeout: int
        :param trial_timeout: timeout in seconds for each trial
        :type trial_timeout: int
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
        """Set the sweep object.

        :param goal: Required. Defines supported metric goals for hyperparameter tuning. Possible values
        include: "minimize", "maximize".
        :type goal: str
        :param primary_metric: Required. Name of the metric to optimize.
        :type primary_metric: str
        """

        if self.objective is None:
            self.objective = Objective()

        if goal:
            self.objective.goal = goal
        if primary_metric:
            self.objective.primary_metric = primary_metric

    @property
    def sampling_algorithm(self) -> Union[str, SamplingAlgorithm]:
        return self._sampling_algorithm

    @sampling_algorithm.setter
    def sampling_algorithm(self, value: Optional[Union[SamplingAlgorithm, str]] = None):
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
        return self._early_termination

    @early_termination.setter
    def early_termination(self, value: Union[EarlyTerminationPolicy, str]):
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
