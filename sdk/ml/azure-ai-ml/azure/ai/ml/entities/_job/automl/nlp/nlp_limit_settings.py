# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import NlpVerticalLimitSettings as RestNlpLimitSettings
from azure.ai.ml._utils.utils import from_iso_duration_format_mins, to_iso_duration_format_mins
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class NlpLimitSettings(RestTranslatableMixin):
    """Limit settings for all AutoML NLP Verticals.

    :param max_concurrent_trials: Maximum number of concurrent AutoML iterations.
    :type max_concurrent_trials: int, optional
    :param max_trials: Maximum number of AutoML iterations.
    :type max_trials: int, optional
    :param timeout_minutes: AutoML job timeout.
    :type timeout_minutes: int, optional
    """

    def __init__(
        self,
        *,
        max_concurrent_trials: Optional[int] = None,
        max_trials: int = 1,
        max_nodes: int = 1,
        timeout_minutes: Optional[int] = None,
        trial_timeout_minutes: Optional[int] = None,
    ):
        self.max_concurrent_trials = max_concurrent_trials
        self.max_trials = max_trials
        self.max_nodes = max_nodes
        self.timeout_minutes = timeout_minutes
        self.trial_timeout_minutes = trial_timeout_minutes

    def _to_rest_object(self) -> RestNlpLimitSettings:
        return RestNlpLimitSettings(
            max_concurrent_trials=self.max_concurrent_trials,
            max_trials=self.max_trials,
            max_nodes=self.max_nodes,
            timeout=to_iso_duration_format_mins(self.timeout_minutes),
            trial_timeout=to_iso_duration_format_mins(self.trial_timeout_minutes),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestNlpLimitSettings) -> "NlpLimitSettings":
        return cls(
            max_concurrent_trials=obj.max_concurrent_trials,
            max_trials=obj.max_trials,
            max_nodes=obj.max_nodes,
            timeout_minutes=from_iso_duration_format_mins(obj.timeout),
            trial_timeout_minutes=from_iso_duration_format_mins(obj.trial_timeout),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NlpLimitSettings):
            return NotImplemented

        return (
            self.max_concurrent_trials == other.max_concurrent_trials
            and self.max_trials == other.max_trials
            and self.max_nodes == other.max_nodes
            and self.timeout_minutes == other.timeout_minutes
            and self.trial_timeout_minutes == other.trial_timeout_minutes
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
