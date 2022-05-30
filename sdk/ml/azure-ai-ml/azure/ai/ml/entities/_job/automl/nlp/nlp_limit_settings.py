# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    NlpVerticalLimitSettings as RestNlpLimitSettings,
)
from azure.ai.ml._utils.utils import (
    to_iso_duration_format_mins,
    from_iso_duration_format_mins,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class NlpLimitSettings(RestTranslatableMixin):
    """Limit settings for all AutoML NLP Verticals."""

    def __init__(
        self,
        *,
        max_concurrent_trials: int = None,
        max_trials: int = 1,
        timeout_minutes: int = None,
    ):
        self.max_concurrent_trials = max_concurrent_trials
        self.max_trials = max_trials
        self.timeout_minutes = timeout_minutes

    def _to_rest_object(self) -> RestNlpLimitSettings:
        return RestNlpLimitSettings(
            max_concurrent_trials=self.max_concurrent_trials,
            max_trials=self.max_trials,
            timeout=to_iso_duration_format_mins(self.timeout_minutes),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestNlpLimitSettings) -> "NlpLimitSettings":
        return cls(
            max_concurrent_trials=obj.max_concurrent_trials,
            max_trials=obj.max_trials,
            timeout_minutes=from_iso_duration_format_mins(obj.timeout),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NlpLimitSettings):
            return NotImplemented

        return (
            self.max_concurrent_trials == other.max_concurrent_trials
            and self.max_trials == other.max_trials
            and self.timeout_minutes == other.timeout_minutes
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
