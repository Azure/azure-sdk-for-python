# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=R0902,protected-access,no-member

from typing import List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import ClassificationModels
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ClassificationTrainingSettings as RestClassificationTrainingSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import ForecastingModels
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ForecastingTrainingSettings as RestForecastingTrainingSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import RegressionModels
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    RegressionTrainingSettings as RestRegressionTrainingSettings,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import TrainingSettings as RestTrainingSettings
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake, from_iso_duration_format_mins, to_iso_duration_format_mins
from azure.ai.ml.constants import TabularTrainingMode
from azure.ai.ml.entities._job.automl.stack_ensemble_settings import StackEnsembleSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class TrainingSettings(RestTranslatableMixin):
    """TrainingSettings class for Azure Machine Learning."""

    def __init__(
        self,
        *,
        enable_onnx_compatible_models: Optional[bool] = None,
        enable_dnn_training: Optional[bool] = None,
        enable_model_explainability: Optional[bool] = None,
        enable_stack_ensemble: Optional[bool] = None,
        enable_vote_ensemble: Optional[bool] = None,
        stack_ensemble_settings: Optional[StackEnsembleSettings] = None,
        ensemble_model_download_timeout: Optional[int] = None,
        allowed_training_algorithms: Optional[List[str]] = None,
        blocked_training_algorithms: Optional[List[str]] = None,
        training_mode: Optional[Union[str, TabularTrainingMode]] = None,
    ):
        """TrainingSettings class for Azure Machine Learning.

        :param enable_onnx_compatible_models: If set to True, the model will be trained to be compatible with ONNX
        :type enable_onnx_compatible_models: typing.Optional[bool]
        :param enable_dnn_training: If set to True,the model will use DNN training
        :type enable_dnn_training: typing.Optional[bool]
        :param enable_model_explainability: If set to True, the model will be trained to be explainable
        :type enable_model_explainability: typing.Optional[bool]
        :param enable_stack_ensemble: If set to True, a final ensemble model will be created using a stack of models
        :type enable_stack_ensemble: typing.Optional[bool]
        :param enable_vote_ensemble: If set to True, a final ensemble model will be created using a voting ensemble
        :type enable_vote_ensemble: typing.Optional[bool]
        :param stack_ensemble_settings: Settings for stack ensemble
        :type stack_ensemble_settings: typing.Optional[azure.ai.ml.automl.StackEnsembleSettings]
        :param ensemble_model_download_timeout: Timeout for downloading ensemble models
        :type ensemble_model_download_timeout: typing.Optional[typing.List[int]]
        :param allowed_training_algorithms: Models to train
        :type allowed_training_algorithms: typing.Optional[typing.List[str]]
        :param blocked_training_algorithms: Models that will not be considered for training
        :type blocked_training_algorithms: typing.Optional[typing.List[str]]
        :param training_mode: [Experimental] The training mode to use.
            The possible values are-

            * distributed- enables distributed training for supported algorithms.

            * non_distributed- disables distributed training.

            * auto- Currently, it is same as non_distributed. In future, this might change.

            Note: This parameter is in public preview and may change in future.
        :type training_mode: typing.Optional[typing.Union[str, azure.ai.ml.constants.TabularTrainingMode]]
        """
        self.enable_onnx_compatible_models = enable_onnx_compatible_models
        self.enable_dnn_training = enable_dnn_training
        self.enable_model_explainability = enable_model_explainability
        self.enable_stack_ensemble = enable_stack_ensemble
        self.enable_vote_ensemble = enable_vote_ensemble
        self.stack_ensemble_settings = stack_ensemble_settings
        self.ensemble_model_download_timeout = ensemble_model_download_timeout
        self.allowed_training_algorithms = allowed_training_algorithms
        self.blocked_training_algorithms = blocked_training_algorithms
        self.training_mode = training_mode

    @experimental
    @property
    def training_mode(self) -> Optional[TabularTrainingMode]:
        return self._training_mode

    @training_mode.setter
    def training_mode(self, value: Optional[Union[str, TabularTrainingMode]]):
        if value is None or value is TabularTrainingMode:
            self._training_mode = value
        elif hasattr(TabularTrainingMode, camel_to_snake(value).upper()):
            self._training_mode = TabularTrainingMode[camel_to_snake(value).upper()]
        else:
            supported_values = ", ".join([f'"{camel_to_snake(mode.value)}"' for mode in TabularTrainingMode])
            msg = (
                f"Unsupported training mode: {value}. Supported values are- {supported_values}. "
                "Or you can use azure.ai.ml.constants.TabularTrainingMode enum."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )

    @property
    def allowed_training_algorithms(self) -> Optional[List[str]]:
        return self._allowed_training_algorithms

    @property
    def blocked_training_algorithms(self) -> Optional[List[str]]:
        return self._blocked_training_algorithms

    def _to_rest_object(self) -> RestTrainingSettings:
        return RestTrainingSettings(
            enable_dnn_training=self.enable_dnn_training,
            enable_onnx_compatible_models=self.enable_onnx_compatible_models,
            enable_model_explainability=self.enable_model_explainability,
            enable_stack_ensemble=self.enable_stack_ensemble,
            enable_vote_ensemble=self.enable_vote_ensemble,
            stack_ensemble_settings=self.stack_ensemble_settings._to_rest_object()
            if self.stack_ensemble_settings
            else None,
            ensemble_model_download_timeout=to_iso_duration_format_mins(self.ensemble_model_download_timeout),
            training_mode=self.training_mode,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestTrainingSettings) -> "TrainingSettings":
        return cls(
            enable_dnn_training=obj.enable_dnn_training,
            enable_onnx_compatible_models=obj.enable_onnx_compatible_models,
            enable_model_explainability=obj.enable_model_explainability,
            enable_stack_ensemble=obj.enable_stack_ensemble,
            enable_vote_ensemble=obj.enable_vote_ensemble,
            ensemble_model_download_timeout=from_iso_duration_format_mins(obj.ensemble_model_download_timeout),
            stack_ensemble_settings=(
                StackEnsembleSettings._from_rest_object(obj.stack_ensemble_settings)
                if obj.stack_ensemble_settings
                else None
            ),
            training_mode=obj.training_mode,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrainingSettings):
            return NotImplemented
        return (
            self.enable_dnn_training == other.enable_dnn_training
            and self.enable_onnx_compatible_models == other.enable_onnx_compatible_models
            and self.enable_model_explainability == other.enable_model_explainability
            and self.enable_stack_ensemble == other.enable_stack_ensemble
            and self.enable_vote_ensemble == other.enable_vote_ensemble
            and self.ensemble_model_download_timeout == other.ensemble_model_download_timeout
            and self.stack_ensemble_settings == other.stack_ensemble_settings
            and self.allowed_training_algorithms == other.allowed_training_algorithms
            and self.blocked_training_algorithms == other.blocked_training_algorithms
            and self.training_mode == other.training_mode
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @blocked_training_algorithms.setter
    def blocked_training_algorithms(self, value):
        self._blocked_training_algorithms = value

    @allowed_training_algorithms.setter
    def allowed_training_algorithms(self, value):
        self._allowed_training_algorithms = value


class ClassificationTrainingSettings(TrainingSettings):
    """Classification TrainingSettings class for Azure Machine Learning."""

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

    @TrainingSettings.allowed_training_algorithms.setter
    def allowed_training_algorithms(self, allowed_model_list: Union[List[str], List[ClassificationModels]]):
        self._allowed_training_algorithms = (
            None
            if allowed_model_list is None
            else [ClassificationModels[camel_to_snake(o)] for o in allowed_model_list]
        )

    @TrainingSettings.blocked_training_algorithms.setter
    def blocked_training_algorithms(self, blocked_model_list: Union[List[str], List[ClassificationModels]]):
        self._blocked_training_algorithms = (
            None
            if blocked_model_list is None
            else [ClassificationModels[camel_to_snake(o)] for o in blocked_model_list]
        )

    def _to_rest_object(self) -> RestClassificationTrainingSettings:
        return RestClassificationTrainingSettings(
            enable_dnn_training=self.enable_dnn_training,
            enable_onnx_compatible_models=self.enable_onnx_compatible_models,
            enable_model_explainability=self.enable_model_explainability,
            enable_stack_ensemble=self.enable_stack_ensemble,
            enable_vote_ensemble=self.enable_vote_ensemble,
            stack_ensemble_settings=self.stack_ensemble_settings,
            ensemble_model_download_timeout=to_iso_duration_format_mins(self.ensemble_model_download_timeout),
            allowed_training_algorithms=self.allowed_training_algorithms,
            blocked_training_algorithms=self.blocked_training_algorithms,
            training_mode=self.training_mode,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestClassificationTrainingSettings) -> "ClassificationTrainingSettings":
        return cls(
            enable_dnn_training=obj.enable_dnn_training,
            enable_onnx_compatible_models=obj.enable_onnx_compatible_models,
            enable_model_explainability=obj.enable_model_explainability,
            enable_stack_ensemble=obj.enable_stack_ensemble,
            enable_vote_ensemble=obj.enable_vote_ensemble,
            ensemble_model_download_timeout=from_iso_duration_format_mins(obj.ensemble_model_download_timeout),
            stack_ensemble_settings=obj.stack_ensemble_settings,
            allowed_training_algorithms=obj.allowed_training_algorithms,
            blocked_training_algorithms=obj.blocked_training_algorithms,
            training_mode=obj.training_mode,
        )


class ForecastingTrainingSettings(TrainingSettings):
    """Forecasting TrainingSettings class for Azure Machine Learning."""

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

    @TrainingSettings.allowed_training_algorithms.setter
    def allowed_training_algorithms(self, allowed_model_list: Union[List[str], List[ForecastingModels]]):
        self._allowed_training_algorithms = (
            None if allowed_model_list is None else [ForecastingModels[camel_to_snake(o)] for o in allowed_model_list]
        )

    @TrainingSettings.blocked_training_algorithms.setter
    def blocked_training_algorithms(self, blocked_model_list: Union[List[str], List[ForecastingModels]]):
        self._blocked_training_algorithms = (
            None if blocked_model_list is None else [ForecastingModels[camel_to_snake(o)] for o in blocked_model_list]
        )

    def _to_rest_object(self) -> RestForecastingTrainingSettings:
        return RestForecastingTrainingSettings(
            enable_dnn_training=self.enable_dnn_training,
            enable_onnx_compatible_models=self.enable_onnx_compatible_models,
            enable_model_explainability=self.enable_model_explainability,
            enable_stack_ensemble=self.enable_stack_ensemble,
            enable_vote_ensemble=self.enable_vote_ensemble,
            stack_ensemble_settings=self.stack_ensemble_settings,
            ensemble_model_download_timeout=to_iso_duration_format_mins(self.ensemble_model_download_timeout),
            allowed_training_algorithms=self.allowed_training_algorithms,
            blocked_training_algorithms=self.blocked_training_algorithms,
            training_mode=self.training_mode,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestForecastingTrainingSettings) -> "ForecastingTrainingSettings":
        return cls(
            enable_dnn_training=obj.enable_dnn_training,
            enable_onnx_compatible_models=obj.enable_onnx_compatible_models,
            enable_model_explainability=obj.enable_model_explainability,
            enable_stack_ensemble=obj.enable_stack_ensemble,
            enable_vote_ensemble=obj.enable_vote_ensemble,
            ensemble_model_download_timeout=from_iso_duration_format_mins(obj.ensemble_model_download_timeout),
            stack_ensemble_settings=obj.stack_ensemble_settings,
            allowed_training_algorithms=obj.allowed_training_algorithms,
            blocked_training_algorithms=obj.blocked_training_algorithms,
            training_mode=obj.training_mode,
        )


class RegressionTrainingSettings(TrainingSettings):
    """Regression TrainingSettings class for Azure Machine Learning."""

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

    @TrainingSettings.allowed_training_algorithms.setter
    def allowed_training_algorithms(self, allowed_model_list: Union[List[str], List[ForecastingModels]]):
        self._allowed_training_algorithms = (
            None if allowed_model_list is None else [RegressionModels[camel_to_snake(o)] for o in allowed_model_list]
        )

    @TrainingSettings.blocked_training_algorithms.setter
    def blocked_training_algorithms(self, blocked_model_list: Union[List[str], List[ForecastingModels]]):
        self._blocked_training_algorithms = (
            None if blocked_model_list is None else [RegressionModels[camel_to_snake(o)] for o in blocked_model_list]
        )

    def _to_rest_object(self) -> RestRegressionTrainingSettings:
        return RestRegressionTrainingSettings(
            enable_dnn_training=self.enable_dnn_training,
            enable_onnx_compatible_models=self.enable_onnx_compatible_models,
            enable_model_explainability=self.enable_model_explainability,
            enable_stack_ensemble=self.enable_stack_ensemble,
            enable_vote_ensemble=self.enable_vote_ensemble,
            stack_ensemble_settings=self.stack_ensemble_settings,
            ensemble_model_download_timeout=to_iso_duration_format_mins(self.ensemble_model_download_timeout),
            allowed_training_algorithms=self.allowed_training_algorithms,
            blocked_training_algorithms=self.blocked_training_algorithms,
            training_mode=self.training_mode,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestRegressionTrainingSettings) -> "RegressionTrainingSettings":
        return cls(
            enable_dnn_training=obj.enable_dnn_training,
            enable_onnx_compatible_models=obj.enable_onnx_compatible_models,
            enable_model_explainability=obj.enable_model_explainability,
            enable_stack_ensemble=obj.enable_stack_ensemble,
            enable_vote_ensemble=obj.enable_vote_ensemble,
            ensemble_model_download_timeout=from_iso_duration_format_mins(obj.ensemble_model_download_timeout),
            stack_ensemble_settings=obj.stack_ensemble_settings,
            allowed_training_algorithms=obj.allowed_training_algorithms,
            blocked_training_algorithms=obj.blocked_training_algorithms,
            training_mode=obj.training_mode,
        )
