# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ImageSweepSettings as RestImageSweepSettings,
    ImageSweepLimitSettings,
    SamplingAlgorithmType,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy


class ImageSweepSettings(RestTranslatableMixin):
    """Sweep settings for all AutoML Image Verticals."""

    def __init__(
        self,
        *,
        sampling_algorithm: Union[str, SamplingAlgorithmType],
        max_concurrent_trials: int = None,
        max_trials: int = None,
        early_termination: EarlyTerminationPolicy = None,
    ):
        self.sampling_algorithm = sampling_algorithm
        self.max_concurrent_trials = max_concurrent_trials
        self.max_trials = max_trials
        self.early_termination = early_termination

    def _to_rest_object(self) -> RestImageSweepSettings:
        return RestImageSweepSettings(
            limits=ImageSweepLimitSettings(
                max_concurrent_trials=self.max_concurrent_trials, max_trials=self.max_trials
            ),
            sampling_algorithm=self.sampling_algorithm,
            early_termination=self.early_termination,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestImageSweepSettings) -> "ImageSweepSettings":
        max_concurrent_trials = None
        max_trials = None
        if obj.limits:
            max_concurrent_trials = obj.limits.max_concurrent_trials
            max_trials = obj.limits.max_trials

        return cls(
            sampling_algorithm=obj.sampling_algorithm,
            max_concurrent_trials=max_concurrent_trials,
            max_trials=max_trials,
            early_termination=EarlyTerminationPolicy._from_rest_object(obj.early_termination)
            if obj.early_termination
            else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageSweepSettings):
            return NotImplemented

        return (
            self.sampling_algorithm == other.sampling_algorithm
            and self.max_concurrent_trials == other.max_concurrent_trials
            and self.max_trials == other.max_trials
            and self.early_termination == other.early_termination
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
