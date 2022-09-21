# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2022_06_01_preview.models import LogVerbosity
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_vertical import AutoMLVertical
from azure.ai.ml.entities._job.automl.nlp.nlp_featurization_settings import NlpFeaturizationSettings
from azure.ai.ml.entities._job.automl.nlp.nlp_limit_settings import NlpLimitSettings
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class AutoMLNLPJob(AutoMLVertical, ABC):
    def __init__(
        self,
        *,
        task_type: str,
        primary_metric: str,
        training_data: Input,
        validation_data: Input,
        target_column_name: Optional[str] = None,
        log_verbosity: Optional[str] = None,
        limits: Optional[NlpLimitSettings] = None,
        featurization: Optional[NlpFeaturizationSettings] = None,
        **kwargs,
    ):
        super().__init__(task_type, training_data=training_data, validation_data=validation_data, **kwargs)
        self.log_verbosity = log_verbosity
        self.primary_metric = primary_metric

        self.target_column_name = target_column_name

        self._limits = limits
        self._featurization = featurization

    @property
    def primary_metric(self):
        return self._primary_metric

    @primary_metric.setter
    def primary_metric(self, value):
        self._primary_metric = value

    @property
    def log_verbosity(self) -> LogVerbosity:
        return self._log_verbosity

    @log_verbosity.setter
    def log_verbosity(self, value: Union[str, LogVerbosity]):
        self._log_verbosity = None if value is None else LogVerbosity[camel_to_snake(value).upper()]

    @property
    def limits(self) -> NlpLimitSettings:
        return self._limits

    @limits.setter
    def limits(self, value: Union[Dict, NlpLimitSettings]) -> None:
        if isinstance(value, NlpLimitSettings):
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
    def featurization(self) -> NlpFeaturizationSettings:
        return self._featurization

    @featurization.setter
    def featurization(self, value: Union[Dict, NlpFeaturizationSettings]) -> None:
        if isinstance(value, NlpFeaturizationSettings):
            self._featurization = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for featurization settings."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_featurization(**value)

    def set_data(self, *, training_data: Input, target_column_name: str, validation_data: Input) -> None:
        # Properties for NlpVerticalDataSettings
        self.target_column_name = target_column_name
        self.training_data = training_data
        self.validation_data = validation_data

    def set_limits(self, *, max_concurrent_trials: Optional[int] = 1, timeout_minutes: int = None) -> None:
        self._limits = NlpLimitSettings(
            max_concurrent_trials=max_concurrent_trials,
            timeout_minutes=timeout_minutes,
        )

    def set_featurization(self, *, dataset_language: Optional[str] = None) -> None:
        self._featurization = NlpFeaturizationSettings(
            dataset_language=dataset_language,
        )

    def _restore_data_inputs(self):
        """Restore MLTableJobInputs to Inputs within data_settings.

        self.training_data and self.validation_data should reflect what
        user passed in (Input) Once we get response back from service
        (as MLTableJobInput), we should set responsible ones back to
        Input
        """
        super()._restore_data_inputs()
        self.training_data = self.training_data if self.training_data else None
        self.validation_data = self.validation_data if self.validation_data else None

    def __eq__(self, other):
        if not isinstance(other, AutoMLNLPJob):
            return NotImplemented

        return (
            self.primary_metric == other.primary_metric
            and self.log_verbosity == other.log_verbosity
            and self.training_data == other.training_data
            and self.validation_data == other.validation_data
            and self._featurization == other._featurization
            and self._limits == other._limits
        )

    def __ne__(self, other):
        return not self.__eq__(other)
