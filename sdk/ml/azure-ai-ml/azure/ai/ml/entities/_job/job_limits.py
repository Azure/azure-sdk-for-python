# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import logging
from typing import Any

from azure.ai.ml._restclient.v2021_10_01.models import CommandJobLimits as RestCommandJobLimits
from azure.ai.ml._restclient.v2021_10_01.models import SweepJobLimits as RestSweepJobLimits
from azure.ai.ml._utils.utils import from_iso_duration_format, to_iso_duration_format
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class CommandJobLimits(RestCommandJobLimits, RestTranslatableMixin):
    """Command Job limit class.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param timeout: The max run duration in seconds, after which the job will be cancelled.
     Only supports duration with precision as low as Seconds.
    :type timeout: int
    """

    def __init__(self, *, timeout: int = None, **kwargs):
        super().__init__(timeout=timeout, **kwargs)

    @property
    def timeout(self) -> int:
        return from_iso_duration_format(self.__dict__["timeout"])

    @timeout.setter
    def timeout(self, value: int) -> None:
        self.__dict__["timeout"] = to_iso_duration_format(value)

    def _to_rest_object(self) -> RestCommandJobLimits:
        return RestCommandJobLimits(**self.__dict__)

    @classmethod
    def _from_rest_object(cls, obj: RestCommandJobLimits) -> "CommandJobLimits":
        if not obj:
            return None

        result = cls()
        result.__dict__.update(obj.as_dict())
        return result


class SweepJobLimits(RestSweepJobLimits, RestTranslatableMixin):
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
        max_concurrent_trials: int = None,
        max_total_trials: int = None,
        timeout: int = None,
        trial_timeout: int = None,
        **kwargs: Any
    ):
        super().__init__(
            max_concurrent_trials=max_concurrent_trials,
            max_total_trials=max_total_trials,
            timeout=timeout,
            trial_timeout=trial_timeout,
            **kwargs
        )

    @property
    def timeout(self) -> int:
        return from_iso_duration_format(self.__dict__["timeout"])

    @timeout.setter
    def timeout(self, value: int) -> None:
        # Bug 1335978:  Service rounds durations less than 60 seconds to 60 days.
        # If duration is non-0 and less than 60, set to 60.
        floored_timeout = value if not value or value > 60 else 60
        self.__dict__["timeout"] = to_iso_duration_format(floored_timeout)

    @property
    def trial_timeout(self) -> int:
        return from_iso_duration_format(self.__dict__["trial_timeout"])

    @trial_timeout.setter
    def trial_timeout(self, value: int) -> None:
        # Bug 1335978:  Service rounds durations less than 60 seconds to 60 days.
        # If duration is non-0 and less than 60, set to 60.
        floored_timeout = value if not value or value > 60 else 60
        self.__dict__["trial_timeout"] = to_iso_duration_format(floored_timeout)

    def _to_rest_object(self) -> RestSweepJobLimits:
        data = copy.deepcopy(self.__dict__)
        data.pop("additional_properties", None)

        return RestSweepJobLimits(**data)

    @classmethod
    def _from_rest_object(cls, obj: RestSweepJobLimits) -> "SweepJobLimits":
        if not obj:
            return None

        result = cls()
        result.__dict__.update(obj.as_dict())
        return result
