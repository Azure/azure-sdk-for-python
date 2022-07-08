# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC
from typing import Dict, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ImageVerticalDataSettings,
    LogVerbosity,
    TrainingDataSettings,
    ImageVerticalValidationDataSettings,
    TestDataSettings,
    SamplingAlgorithmType,
)
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_vertical import AutoMLVertical
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.entities._job.automl.image.image_limit_settings import ImageLimitSettings
from azure.ai.ml.entities._job.automl.image.image_sweep_settings import ImageSweepSettings
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


class AutoMLImage(AutoMLVertical, ABC):
    def __init__(
        self,
        *,
        task_type: str,
        data: ImageVerticalDataSettings = None,
        limits: ImageLimitSettings = None,
        sweep: ImageSweepSettings = None,
        **kwargs,
    ) -> None:
        self.log_verbosity = kwargs.pop("log_verbosity", LogVerbosity.INFO)
        super().__init__(task_type=task_type, **kwargs)

        self._data = data
        # Set default value for self._limits as it is a required property in rest object.
        self._limits = limits or ImageLimitSettings()
        self._sweep = sweep

    @property
    def log_verbosity(self) -> LogVerbosity:
        return self._log_verbosity

    @log_verbosity.setter
    def log_verbosity(self, value: Union[str, LogVerbosity]):
        self._log_verbosity = None if value is None else LogVerbosity[camel_to_snake(value).upper()]

    @property
    def limits(self) -> ImageLimitSettings:
        return self._limits

    @limits.setter
    def limits(self, value: Union[Dict, ImageLimitSettings]) -> None:
        if isinstance(value, ImageLimitSettings):
            self._limits = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for limit settings."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_limits(**value)

    @property
    def sweep(self) -> ImageSweepSettings:
        return self._sweep

    @sweep.setter
    def sweep(self, value: Union[Dict, ImageSweepSettings]) -> None:
        if isinstance(value, ImageSweepSettings):
            self._sweep = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for sweep settings."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_sweep(**value)

    def set_data(
        self,
        *,
        training_data: Input,
        target_column_name: str,
        validation_data: Input = None,
        validation_data_size: float = None,
    ) -> None:
        self._data = ImageVerticalDataSettings(
            target_column_name=target_column_name, training_data=TrainingDataSettings(data=training_data)
        )

        self._data.validation_data = self._data.validation_data or ImageVerticalValidationDataSettings()
        self._data.validation_data.data = validation_data or self._data.validation_data.data
        self._data.validation_data.validation_data_size = (
            validation_data_size
            if validation_data_size is not None
            else self._data.validation_data.validation_data_size
        )

    def set_limits(
        self,
        *,
        timeout_minutes: int = None,
    ) -> None:
        self._limits = self._limits or ImageLimitSettings()
        self._limits.timeout_minutes = timeout_minutes if timeout_minutes is not None else self._limits.timeout_minutes

    def set_sweep(
        self,
        *,
        sampling_algorithm: Union[str, SamplingAlgorithmType],
        max_concurrent_trials: int = None,
        max_trials: int = None,
        early_termination: EarlyTerminationPolicy = None,
    ) -> None:
        if self._sweep:
            self._sweep.sampling_algorithm = sampling_algorithm
        else:
            self._sweep = ImageSweepSettings(sampling_algorithm=sampling_algorithm)

        self._sweep.max_concurrent_trials = (
            max_concurrent_trials if max_concurrent_trials is not None else self._sweep.max_concurrent_trials
        )
        self._sweep.max_trials = max_trials if max_trials is not None else self._sweep.max_trials
        self._sweep.early_termination = early_termination or self._sweep.early_termination

    def __eq__(self, other) -> bool:
        if not isinstance(other, AutoMLImage):
            return NotImplemented

        return self._data == other._data and self._limits == other._limits and self._sweep == other._sweep

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
