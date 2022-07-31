# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ImageVerticalDataSettings,
    ImageModelSettingsObjectDetection,
    LearningRateScheduler,
    StochasticOptimizer,
    ModelSize,
    ValidationMetricType,
)
from azure.ai.ml.entities._job.automl.image.automl_image import AutoMLImage
from azure.ai.ml.entities._job.automl.image.image_limit_settings import ImageLimitSettings
from azure.ai.ml.entities._job.automl.image.image_object_detection_search_space import (
    ImageObjectDetectionSearchSpace,
)
from azure.ai.ml.entities._job.automl.image.image_sweep_settings import ImageSweepSettings
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


class AutoMLImageObjectDetectionBase(AutoMLImage):
    def __init__(
        self,
        *,
        task_type: str,
        data: ImageVerticalDataSettings = None,
        limits: ImageLimitSettings = None,
        sweep: ImageSweepSettings = None,
        image_model: ImageModelSettingsObjectDetection = None,
        search_space: List[ImageObjectDetectionSearchSpace] = None,
        **kwargs,
    ) -> None:
        super().__init__(task_type=task_type, data=data, limits=limits, sweep=sweep, **kwargs)

        self._image_model = image_model
        self._search_space = search_space

    @property
    def image_model(self) -> ImageModelSettingsObjectDetection:
        return self._image_model

    @image_model.setter
    def image_model(self, value: Union[Dict, ImageModelSettingsObjectDetection]) -> None:
        if isinstance(value, ImageModelSettingsObjectDetection):
            self._image_model = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for model settings."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_image_model(**value)

    @property
    def search_space(self) -> List[ImageObjectDetectionSearchSpace]:
        return self._search_space

    @search_space.setter
    def search_space(self, value: Union[List[Dict], List[ImageObjectDetectionSearchSpace]]) -> None:
        if not isinstance(value, list):
            msg = "Expected a list for search space."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )

        all_dict_type = all(isinstance(item, dict) for item in value)
        all_search_space_type = all(isinstance(item, ImageObjectDetectionSearchSpace) for item in value)

        if all_search_space_type:
            self._search_space = value
        elif all_dict_type:
            self._search_space = [ImageObjectDetectionSearchSpace(**item) for item in value]
        else:
            msg = "Expected all items in the list to be either dictionaries or ImageObjectDetectionSearchSpace objects."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )

    def set_image_model(
        self,
        *,
        advanced_settings: str = None,
        ams_gradient: bool = None,
        augmentations: str = None,
        beta1: float = None,
        beta2: float = None,
        checkpoint_dataset_id: str = None,
        checkpoint_filename: str = None,
        checkpoint_frequency: int = None,
        checkpoint_run_id: str = None,
        distributed: bool = None,
        early_stopping: bool = None,
        early_stopping_delay: int = None,
        early_stopping_patience: int = None,
        enable_onnx_normalization: bool = None,
        evaluation_frequency: int = None,
        gradient_accumulation_step: int = None,
        layers_to_freeze: int = None,
        learning_rate: float = None,
        learning_rate_scheduler: Union[str, LearningRateScheduler] = None,
        model_name: str = None,
        momentum: float = None,
        nesterov: bool = None,
        number_of_epochs: int = None,
        number_of_workers: int = None,
        optimizer: Union[str, StochasticOptimizer] = None,
        random_seed: int = None,
        step_lr_gamma: float = None,
        step_lr_step_size: int = None,
        training_batch_size: int = None,
        validation_batch_size: int = None,
        warmup_cosine_lr_cycles: float = None,
        warmup_cosine_lr_warmup_epochs: int = None,
        weight_decay: float = None,
        box_detections_per_image: int = None,
        box_score_threshold: float = None,
        image_size: int = None,
        max_size: int = None,
        min_size: int = None,
        model_size: Union[str, ModelSize] = None,
        multi_scale: bool = None,
        nms_iou_threshold: float = None,
        tile_grid_size: str = None,
        tile_overlap_ratio: float = None,
        tile_predictions_nms_threshold: float = None,
        validation_iou_threshold: float = None,
        validation_metric_type: Union[str, ValidationMetricType] = None,
    ) -> None:
        self._image_model = self._image_model or ImageModelSettingsObjectDetection()

        self._image_model.advanced_settings = (
            advanced_settings if advanced_settings is not None else self._image_model.advanced_settings
        )
        self._image_model.ams_gradient = ams_gradient if ams_gradient is not None else self._image_model.ams_gradient
        self._image_model.augmentations = (
            augmentations if augmentations is not None else self._image_model.augmentations
        )
        self._image_model.beta1 = beta1 if beta1 is not None else self._image_model.beta1
        self._image_model.beta2 = beta2 if beta2 is not None else self._image_model.beta2
        self._image_model.checkpoint_dataset_id = (
            checkpoint_dataset_id if checkpoint_dataset_id is not None else self._image_model.checkpoint_dataset_id
        )
        self._image_model.checkpoint_filename = (
            checkpoint_filename if checkpoint_filename is not None else self._image_model.checkpoint_filename
        )
        self._image_model.checkpoint_frequency = (
            checkpoint_frequency if checkpoint_frequency is not None else self._image_model.checkpoint_frequency
        )
        self._image_model.checkpoint_run_id = (
            checkpoint_run_id if checkpoint_run_id is not None else self._image_model.checkpoint_run_id
        )
        self._image_model.distributed = distributed if distributed is not None else self._image_model.distributed
        self._image_model.early_stopping = (
            early_stopping if early_stopping is not None else self._image_model.early_stopping
        )
        self._image_model.early_stopping_delay = (
            early_stopping_delay if early_stopping_delay is not None else self._image_model.early_stopping_delay
        )
        self._image_model.early_stopping_patience = (
            early_stopping_patience
            if early_stopping_patience is not None
            else self._image_model.early_stopping_patience
        )
        self._image_model.enable_onnx_normalization = (
            enable_onnx_normalization
            if enable_onnx_normalization is not None
            else self._image_model.enable_onnx_normalization
        )
        self._image_model.evaluation_frequency = (
            evaluation_frequency if evaluation_frequency is not None else self._image_model.evaluation_frequency
        )
        self._image_model.gradient_accumulation_step = (
            gradient_accumulation_step
            if gradient_accumulation_step is not None
            else self._image_model.gradient_accumulation_step
        )
        self._image_model.layers_to_freeze = (
            layers_to_freeze if layers_to_freeze is not None else self._image_model.layers_to_freeze
        )
        self._image_model.learning_rate = (
            learning_rate if learning_rate is not None else self._image_model.learning_rate
        )
        self._image_model.learning_rate_scheduler = (
            learning_rate_scheduler
            if learning_rate_scheduler is not None
            else self._image_model.learning_rate_scheduler
        )
        self._image_model.model_name = model_name if model_name is not None else self._image_model.model_name
        self._image_model.momentum = momentum if momentum is not None else self._image_model.momentum
        self._image_model.nesterov = nesterov if nesterov is not None else self._image_model.nesterov
        self._image_model.number_of_epochs = (
            number_of_epochs if number_of_epochs is not None else self._image_model.number_of_epochs
        )
        self._image_model.number_of_workers = (
            number_of_workers if number_of_workers is not None else self._image_model.number_of_workers
        )
        self._image_model.optimizer = optimizer if optimizer is not None else self._image_model.optimizer
        self._image_model.random_seed = random_seed if random_seed is not None else self._image_model.random_seed
        self._image_model.step_lr_gamma = (
            step_lr_gamma if step_lr_gamma is not None else self._image_model.step_lr_gamma
        )
        self._image_model.step_lr_step_size = (
            step_lr_step_size if step_lr_step_size is not None else self._image_model.step_lr_step_size
        )
        self._image_model.training_batch_size = (
            training_batch_size if training_batch_size is not None else self._image_model.training_batch_size
        )
        self._image_model.validation_batch_size = (
            validation_batch_size if validation_batch_size is not None else self._image_model.validation_batch_size
        )
        self._image_model.warmup_cosine_lr_cycles = (
            warmup_cosine_lr_cycles
            if warmup_cosine_lr_cycles is not None
            else self._image_model.warmup_cosine_lr_cycles
        )
        self._image_model.warmup_cosine_lr_warmup_epochs = (
            warmup_cosine_lr_warmup_epochs
            if warmup_cosine_lr_warmup_epochs is not None
            else self._image_model.warmup_cosine_lr_warmup_epochs
        )
        self._image_model.weight_decay = weight_decay if weight_decay is not None else self._image_model.weight_decay
        self._image_model.box_detections_per_image = (
            box_detections_per_image
            if box_detections_per_image is not None
            else self._image_model.box_detections_per_image
        )
        self._image_model.box_score_threshold = (
            box_score_threshold if box_score_threshold is not None else self._image_model.box_score_threshold
        )
        self._image_model.image_size = image_size if image_size is not None else self._image_model.image_size
        self._image_model.max_size = max_size if max_size is not None else self._image_model.max_size
        self._image_model.min_size = min_size if min_size is not None else self._image_model.min_size
        self._image_model.model_size = model_size if model_size is not None else self._image_model.model_size
        self._image_model.multi_scale = multi_scale if multi_scale is not None else self._image_model.multi_scale
        self._image_model.nms_iou_threshold = (
            nms_iou_threshold if nms_iou_threshold is not None else self._image_model.nms_iou_threshold
        )
        self._image_model.tile_grid_size = (
            tile_grid_size if tile_grid_size is not None else self._image_model.tile_grid_size
        )
        self._image_model.tile_overlap_ratio = (
            tile_overlap_ratio if tile_overlap_ratio is not None else self._image_model.tile_overlap_ratio
        )
        self._image_model.tile_predictions_nms_threshold = (
            tile_predictions_nms_threshold
            if tile_predictions_nms_threshold is not None
            else self._image_model.tile_predictions_nms_threshold
        )
        self._image_model.validation_iou_threshold = (
            validation_iou_threshold
            if validation_iou_threshold is not None
            else self._image_model.validation_iou_threshold
        )
        self._image_model.validation_metric_type = (
            validation_metric_type if validation_metric_type is not None else self._image_model.validation_metric_type
        )

    def extend_search_space(
        self,
        value: Union[ImageObjectDetectionSearchSpace, List[ImageObjectDetectionSearchSpace]],
    ) -> None:
        self._search_space = self._search_space or []

        if isinstance(value, list):
            self._search_space.extend(value)
        else:
            self._search_space.append(value)

    @classmethod
    def _get_search_space_from_str(cls, search_space_str: str):
        return (
            [
                ImageObjectDetectionSearchSpace._from_rest_object(entry)
                for entry in search_space_str
                if entry is not None
            ]
            if search_space_str is not None
            else None
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, AutoMLImageObjectDetectionBase):
            return NotImplemented

        if not super().__eq__(other):
            return False

        return self._image_model == other._image_model and self._search_space == other._search_space

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
