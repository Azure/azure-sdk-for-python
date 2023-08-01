# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import TableVerticalLimitSettings as RestTabularLimitSettings
from azure.ai.ml._utils.utils import from_iso_duration_format_mins, to_iso_duration_format_mins
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class TabularLimitSettings(RestTranslatableMixin):
    """Limit settings for a AutoML Table Verticals.

    :param enable_early_termination: Whether to enable early termination if the score is not improving in
        the short term. The default is True.
    :type enable_early_termination: bool, optional
    :param exit_score: Target score for experiment. The experiment terminates after this score is reached.
    :type exit_score: float, optional
    :param max_concurrent_trials: Maximum number of concurrent AutoML iterations.
    :type max_concurrent_trials: int, optional
    :param max_cores_per_trial: The maximum number of threads to use for a given training iteration.
    :type max_cores_per_trial: int, optional
    :param max_nodes: [Experimental] The maximum number of nodes to use for distributed training.

        * For forecasting, each model is trained using max(2, int(max_nodes / max_concurrent_trials)) nodes.

        * For classification/regression, each model is trained using max_nodes nodes.

        Note- This parameter is in public preview and might change in future.
    :type max_nodes: int, optional
    :param max_trials: Maximum number of AutoML iterations.
    :type max_trials: int, optional
    :param timeout_minutes: AutoML job timeout.
    :type timeout_minutes: int, optional
    :param trial_timeout_minutes: AutoML job timeout.
    :type trial_timeout_minutes: int, optional
    """

    def __init__(
        self,
        *,
        enable_early_termination: Optional[bool] = None,
        exit_score: Optional[float] = None,
        max_concurrent_trials: Optional[int] = None,
        max_cores_per_trial: Optional[int] = None,
        max_nodes: Optional[int] = None,
        max_trials: Optional[int] = None,
        timeout_minutes: Optional[int] = None,
        trial_timeout_minutes: Optional[int] = None,
    ):
        self.enable_early_termination = enable_early_termination
        self.exit_score = exit_score
        self.max_concurrent_trials = max_concurrent_trials
        self.max_cores_per_trial = max_cores_per_trial
        self.max_nodes = max_nodes
        self.max_trials = max_trials
        self.timeout_minutes = timeout_minutes
        self.trial_timeout_minutes = trial_timeout_minutes

    def _to_rest_object(self) -> RestTabularLimitSettings:
        return RestTabularLimitSettings(
            enable_early_termination=self.enable_early_termination,
            exit_score=self.exit_score,
            max_concurrent_trials=self.max_concurrent_trials,
            max_cores_per_trial=self.max_cores_per_trial,
            max_nodes=self.max_nodes,
            max_trials=self.max_trials,
            timeout=to_iso_duration_format_mins(self.timeout_minutes),
            trial_timeout=to_iso_duration_format_mins(self.trial_timeout_minutes),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestTabularLimitSettings) -> "TabularLimitSettings":
        return cls(
            enable_early_termination=obj.enable_early_termination,
            exit_score=obj.exit_score,
            max_concurrent_trials=obj.max_concurrent_trials,
            max_cores_per_trial=obj.max_cores_per_trial,
            max_nodes=obj.max_nodes,
            max_trials=obj.max_trials,
            timeout_minutes=from_iso_duration_format_mins(obj.timeout),
            trial_timeout_minutes=from_iso_duration_format_mins(obj.trial_timeout),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TabularLimitSettings):
            return NotImplemented
        return (
            self.enable_early_termination == other.enable_early_termination
            and self.exit_score == other.exit_score
            and self.max_concurrent_trials == other.max_concurrent_trials
            and self.max_cores_per_trial == other.max_cores_per_trial
            and self.max_nodes == other.max_nodes
            and self.max_trials == other.max_trials
            and self.timeout_minutes == other.timeout_minutes
            and self.trial_timeout_minutes == other.trial_timeout_minutes
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
