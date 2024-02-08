# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from abc import ABC
from typing import Any, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import CommandJobLimits as RestCommandJobLimits
from azure.ai.ml._restclient.v2023_08_01_preview.models import SweepJobLimits as RestSweepJobLimits
from azure.ai.ml._utils.utils import from_iso_duration_format, is_data_binding_expression, to_iso_duration_format
from azure.ai.ml.constants import JobType
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class JobLimits(RestTranslatableMixin, ABC):
    """Base class for Job limits.

    This class should not be instantiated directly. Instead, one of its child classes should be used.
    """

    def __init__(
        self,
    ) -> None:
        self.type: Any = None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, JobLimits):
            return NotImplemented
        res: bool = self._to_rest_object() == other._to_rest_object()
        return res


class CommandJobLimits(JobLimits):
    """Limits for Command Jobs.

    :keyword timeout: The maximum run duration, in seconds, after which the job will be cancelled.
    :paramtype timeout: Optional[Union[int, str]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_command_configurations.py
            :start-after: [START command_job_definition]
            :end-before: [END command_job_definition]
            :language: python
            :dedent: 8
            :caption: Configuring a CommandJob with CommandJobLimits.
    """

    def __init__(self, *, timeout: Optional[Union[int, str]] = None) -> None:
        super().__init__()
        self.type = JobType.COMMAND
        self.timeout = timeout

    def _to_rest_object(self) -> RestCommandJobLimits:
        if is_data_binding_expression(self.timeout):
            return RestCommandJobLimits(timeout=self.timeout)
        return RestCommandJobLimits(timeout=to_iso_duration_format(self.timeout))

    @classmethod
    def _from_rest_object(cls, obj: Union[RestCommandJobLimits, dict]) -> Optional["CommandJobLimits"]:
        if not obj:
            return None
        if isinstance(obj, dict):
            timeout_value = obj.get("timeout", None)
            # if timeout value is a binding string
            if is_data_binding_expression(timeout_value):
                return cls(timeout=timeout_value)
            # if response timeout is a normal iso date string
            obj = RestCommandJobLimits.from_dict(obj)
        return cls(timeout=from_iso_duration_format(obj.timeout))


class SweepJobLimits(JobLimits):
    """Limits for Sweep Jobs.

    :keyword max_concurrent_trials: The maximum number of concurrent trials for the Sweep Job.
    :paramtype max_concurrent_trials: Optional[int]
    :keyword max_total_trials: The maximum number of total trials for the Sweep Job.
    :paramtype max_total_trials: Optional[int]
    :keyword timeout: The maximum run duration, in seconds, after which the job will be cancelled.
    :paramtype timeout: Optional[int]
    :keyword trial_timeout: The timeout value, in seconds, for each Sweep Job trial.
    :paramtype trial_timeout: Optional[int]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_bayesian_sampling_algorithm]
            :end-before: [END configure_sweep_job_bayesian_sampling_algorithm]
            :language: python
            :dedent: 8
            :caption: Assigning limits to a SweepJob
    """

    def __init__(
        self,
        *,
        max_concurrent_trials: Optional[int] = None,
        max_total_trials: Optional[int] = None,
        timeout: Optional[int] = None,
        trial_timeout: Optional[Union[int, str]] = None,
    ) -> None:
        super().__init__()
        self.type = JobType.SWEEP
        self.max_concurrent_trials = max_concurrent_trials
        self.max_total_trials = max_total_trials
        self._timeout = _get_floored_timeout(timeout)
        self._trial_timeout = _get_floored_timeout(trial_timeout)

    @property
    def timeout(self) -> Optional[Union[int, str]]:
        """The maximum run duration, in seconds, after which the job will be cancelled.

        :return: The maximum run duration, in seconds, after which the job will be cancelled.
        :rtype: int
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: int) -> None:
        """Sets the maximum run duration.

        :param value: The maximum run duration, in seconds, after which the job will be cancelled.
        :type value: int
        """
        self._timeout = _get_floored_timeout(value)

    @property
    def trial_timeout(self) -> Optional[Union[int, str]]:
        """The timeout value, in seconds, for each Sweep Job trial.

        :return: The timeout value, in seconds, for each Sweep Job trial.
        :rtype: int
        """
        return self._trial_timeout

    @trial_timeout.setter
    def trial_timeout(self, value: int) -> None:
        """Sets the timeout value for each Sweep Job trial.

        :param value: The timeout value, in seconds, for each Sweep Job trial.
        :type value: int
        """
        self._trial_timeout = _get_floored_timeout(value)

    def _to_rest_object(self) -> RestSweepJobLimits:
        return RestSweepJobLimits(
            max_concurrent_trials=self.max_concurrent_trials,
            max_total_trials=self.max_total_trials,
            timeout=to_iso_duration_format(self.timeout),
            trial_timeout=to_iso_duration_format(self.trial_timeout),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestSweepJobLimits) -> Optional["SweepJobLimits"]:
        if not obj:
            return None

        return cls(
            max_concurrent_trials=obj.max_concurrent_trials,
            max_total_trials=obj.max_total_trials,
            timeout=from_iso_duration_format(obj.timeout),
            trial_timeout=from_iso_duration_format(obj.trial_timeout),
        )


def _get_floored_timeout(value: Optional[Union[int, str]]) -> Optional[Union[int, str]]:
    # Bug 1335978:  Service rounds durations less than 60 seconds to 60 days.
    # If duration is non-0 and less than 60, set to 60.
    if isinstance(value, int):
        return value if not value or value > 60 else 60

    return None


class DoWhileJobLimits(JobLimits):
    """DoWhile Job limit class.

    :keyword max_iteration_count: The maximum number of iterations for the DoWhile Job.
    :paramtype max_iteration_count: Optional[int]
    """

    def __init__(
        self,  # pylint: disable=unused-argument
        *,
        max_iteration_count: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self._max_iteration_count = max_iteration_count

    @property
    def max_iteration_count(self) -> Optional[int]:
        """The maximum number of iterations for the DoWhile Job.

        :rtype: int
        """
        return self._max_iteration_count
