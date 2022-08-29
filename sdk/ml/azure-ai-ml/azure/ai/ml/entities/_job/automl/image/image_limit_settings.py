# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_02_01_preview.models import ImageLimitSettings as RestImageLimitSettings
from azure.ai.ml._utils.utils import from_iso_duration_format_mins, to_iso_duration_format_mins
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageLimitSettings(RestTranslatableMixin):
    """Limit settings for all AutoML Image Verticals.

    :param max_concurrent_trials: Maximum number of concurrent AutoML iterations.
    :type max_concurrent_trials: int
    :param max_trials: Maximum number of AutoML iterations.
    :type max_trials: int
    :param timeout: AutoML job timeout.
    :type timeout: ~datetime.timedelta
    """

    def __init__(
        self,
        *,
        max_concurrent_trials: int = None,
        max_trials: int = None,
        timeout_minutes: int = None,
    ):
        self.max_concurrent_trials = max_concurrent_trials
        self.max_trials = max_trials
        self.timeout_minutes = timeout_minutes

    def _to_rest_object(self) -> RestImageLimitSettings:
        return RestImageLimitSettings(
            max_concurrent_trials=self.max_concurrent_trials,
            max_trials=self.max_trials,
            timeout=to_iso_duration_format_mins(self.timeout_minutes),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestImageLimitSettings) -> "ImageLimitSettings":
        return cls(
            max_concurrent_trials=obj.max_concurrent_trials,
            max_trials=obj.max_trials,
            timeout_minutes=from_iso_duration_format_mins(obj.timeout),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageLimitSettings):
            return NotImplemented

        return (
            self.max_concurrent_trials == other.max_concurrent_trials
            and self.max_trials == other.max_trials
            and self.timeout_minutes == other.timeout_minutes
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
