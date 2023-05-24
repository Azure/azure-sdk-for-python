# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from abc import ABC
from typing import Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    CommandJobLimits as RestCommandJobLimits,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    SweepJobLimits as RestSweepJobLimits,
)
from azure.ai.ml._utils.utils import (
    from_iso_duration_format,
    is_data_binding_expression,
    to_iso_duration_format,
)
from azure.ai.ml.constants import JobType
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class JobLimits(RestTranslatableMixin, ABC):
    def __init__(
        self,
    ):
        self.type = None

    def __eq__(self, other) -> bool:
        if not isinstance(other, JobLimits):
            return NotImplemented
        return self._to_rest_object() == other._to_rest_object()


class CommandJobLimits(JobLimits):
    """Command Job limit class.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param timeout: The max run duration in seconds, after which the job will be cancelled.
     Only supports duration with precision as low as Seconds.
    :type timeout: int
    """

    def __init__(self, *, timeout: Union[int, str, None] = None):
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
    """Sweep Job limit class.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param max_concurrent_trials: Sweep Job max concurrent trials.
    :type max_concurrent_trials: int
    :param max_total_trials: Sweep Job max total trials.
    :type max_total_trials: int
    :param timeout: The max run duration in seconds , after which the job will be cancelled.
     Only supports duration with precision as low as Seconds.
    :type timeout: int
    :param trial_timeout: Sweep Job Trial timeout value in seconds.
    :type trial_timeout: int
    """

    def __init__(
        self,
        *,
        max_concurrent_trials: Optional[int] = None,
        max_total_trials: Optional[int] = None,
        timeout: Optional[int] = None,
        trial_timeout: Optional[int] = None,
    ):
        super().__init__()
        self.type = JobType.SWEEP
        self.max_concurrent_trials = max_concurrent_trials
        self.max_total_trials = max_total_trials
        self._timeout = _get_floored_timeout(timeout)
        self._trial_timeout = _get_floored_timeout(trial_timeout)

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, value: int) -> None:
        self._timeout = _get_floored_timeout(value)

    @property
    def trial_timeout(self) -> int:
        return self._trial_timeout

    @trial_timeout.setter
    def trial_timeout(self, value: int) -> None:
        self._trial_timeout = _get_floored_timeout(value)

    def _to_rest_object(self) -> RestSweepJobLimits:
        return RestSweepJobLimits(
            max_concurrent_trials=self.max_concurrent_trials,
            max_total_trials=self.max_total_trials,
            timeout=to_iso_duration_format(self.timeout),
            trial_timeout=to_iso_duration_format(self.trial_timeout),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestSweepJobLimits) -> "SweepJobLimits":
        if not obj:
            return None

        return cls(
            max_concurrent_trials=obj.max_concurrent_trials,
            max_total_trials=obj.max_total_trials,
            timeout=from_iso_duration_format(obj.timeout),
            trial_timeout=from_iso_duration_format(obj.trial_timeout),
        )


def _get_floored_timeout(value: int) -> int:
    # Bug 1335978:  Service rounds durations less than 60 seconds to 60 days.
    # If duration is non-0 and less than 60, set to 60.
    return value if not value or value > 60 else 60


class DoWhileJobLimits(JobLimits):
    """DoWhile Job limit class.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param max_iteration_count:
    :type max_iteration_count: int
    """

    def __init__(
        self,
        *,
        max_iteration_count: Optional[int] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        super().__init__()
        self._max_iteration_count = max_iteration_count

    @property
    def max_iteration_count(self) -> int:
        return self._max_iteration_count
