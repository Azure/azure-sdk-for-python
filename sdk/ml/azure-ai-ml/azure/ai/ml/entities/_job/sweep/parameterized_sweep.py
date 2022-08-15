# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable, Dict, Optional, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._schema.job.loadable_mixin import LoadableMixin

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
from .search_space import SweepDistribution

SAMPLING_ALGORITHM_TO_REST_CONSTRUCTOR: Dict[SamplingAlgorithmType, Callable[[], RestSamplingAlgorithm]] = {
    SamplingAlgorithmType.RANDOM: lambda: RestRandomSamplingAlgorithm(),
    SamplingAlgorithmType.GRID: lambda: RestGridSamplingAlgorithm(),
    SamplingAlgorithmType.BAYESIAN: lambda: RestBayesianSamplingAlgorithm(),
}

SAMPLING_ALGORITHM_CONSTRUCTOR: Dict[SamplingAlgorithmType, Callable[[], SamplingAlgorithm]] = {
    SamplingAlgorithmType.RANDOM: lambda: RandomSamplingAlgorithm(),
    SamplingAlgorithmType.GRID: lambda: GridSamplingAlgorithm(),
    SamplingAlgorithmType.BAYESIAN: lambda: BayesianSamplingAlgorithm(),
}


class ParameterizedSweep(LoadableMixin):
    """Shared logic for standalone and pipeline sweep job."""

    def __init__(
        self,
        limits: SweepJobLimits = None,
        sampling_algorithm: Union[str, SamplingAlgorithm] = None,
        objective: Optional[Union[Dict, Objective]] = None,
        early_termination: EarlyTerminationPolicy = None,
        search_space: Dict[str, SweepDistribution] = None,
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
            )
        self._limits = value

    def set_limits(
        self,
        *,
        max_concurrent_trials: int = None,
        max_total_trials: int = None,
        timeout: int = None,
        trial_timeout: int = None,
    ) -> None:
        """Set limits for Sweep node. Leave parameters as None if you don't
        want to update corresponding values.

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

    def set_objective(self, *, goal: str = None, primary_metric: str = None) -> None:
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
            )

    def _get_rest_sampling_algorithm(self) -> RestSamplingAlgorithm:
        # TODO: self.sampling_algorithm will always return SamplingAlgorithm
        if isinstance(self.sampling_algorithm, SamplingAlgorithm):
            return self.sampling_algorithm
        elif isinstance(self.sampling_algorithm, str):
            return SAMPLING_ALGORITHM_CONSTRUCTOR[SamplingAlgorithmType(self.sampling_algorithm.lower().capitalize())]()
        msg = f"Received unsupported value {self._sampling_algorithm} as the sampling algorithm"
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.SWEEP_JOB,
            error_category=ErrorCategory.USER_ERROR,
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
                )
        else:
            msg = f"Received unsupported value of type {type(value)} as the early termination policy"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SWEEP_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )

    def _override_missing_properties_from_trial(self):
        return
