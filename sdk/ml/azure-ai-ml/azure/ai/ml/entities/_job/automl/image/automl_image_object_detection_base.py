# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    LearningRateScheduler,
    ModelSize,
    StochasticOptimizer,
    ValidationMetricType,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._job.automl import SearchSpace
from azure.ai.ml.entities._job.automl.image.automl_image import AutoMLImage
from azure.ai.ml.entities._job.automl.image.image_limit_settings import ImageLimitSettings
from azure.ai.ml.entities._job.automl.image.image_model_settings import ImageModelSettingsObjectDetection
from azure.ai.ml.entities._job.automl.image.image_object_detection_search_space import ImageObjectDetectionSearchSpace
from azure.ai.ml.entities._job.automl.image.image_sweep_settings import ImageSweepSettings
from azure.ai.ml.entities._job.automl.utils import cast_to_specific_search_space
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class AutoMLImageObjectDetectionBase(AutoMLImage):
    def __init__(
        self,
        *,
        task_type: str,
        limits: Optional[ImageLimitSettings] = None,
        sweep: Optional[ImageSweepSettings] = None,
        training_parameters: Optional[ImageModelSettingsObjectDetection] = None,
        search_space: Optional[List[ImageObjectDetectionSearchSpace]] = None,
        **kwargs,
    ) -> None:
        super().__init__(task_type=task_type, limits=limits, sweep=sweep, **kwargs)

        self.training_parameters = training_parameters  # Assigning training_parameters through setter method.
        self._search_space = search_space

    @property
    def training_parameters(self) -> ImageModelSettingsObjectDetection:
        return self._training_parameters

    @training_parameters.setter
    def training_parameters(self, value: Union[Dict, ImageModelSettingsObjectDetection]) -> None:
        if value is None:
            self._training_parameters = None
        elif isinstance(value, ImageModelSettingsObjectDetection):
            self._training_parameters = value
            # set_training_parameters convert parameter values from snake case str to enum.
            # We need to add any future enum parameters in this call to support snake case str.
            self.set_training_parameters(
                optimizer=value.optimizer,
                learning_rate_scheduler=value.learning_rate_scheduler,
                model_size=value.model_size,
                validation_metric_type=value.validation_metric_type,
            )
        elif value is None:
            self._training_parameters = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for model settings."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_training_parameters(**value)

    @property
    def search_space(self) -> List[ImageObjectDetectionSearchSpace]:
        return self._search_space

    @search_space.setter
    def search_space(self, value: Union[List[Dict], List[SearchSpace]]) -> None:
        if not isinstance(value, list):
            msg = "Expected a list for search space."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )

        all_dict_type = all(isinstance(item, dict) for item in value)
        all_search_space_type = all(isinstance(item, SearchSpace) for item in value)

        if all_search_space_type or all_dict_type:
            self._search_space = [
                cast_to_specific_search_space(item, ImageObjectDetectionSearchSpace, self.task_type) for item in value
            ]
        else:
            msg = "Expected all items in the list to be either dictionaries or SearchSpace objects."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )

    # pylint: disable=too-many-locals
    def set_training_parameters(
        self,
        *,
        advanced_settings: Optional[str] = None,
        ams_gradient: Optional[bool] = None,
        beta1: Optional[float] = None,
        beta2: Optional[float] = None,
        checkpoint_frequency: Optional[int] = None,
        checkpoint_run_id: Optional[str] = None,
        distributed: Optional[bool] = None,
        early_stopping: Optional[bool] = None,
        early_stopping_delay: Optional[int] = None,
        early_stopping_patience: Optional[int] = None,
        enable_onnx_normalization: Optional[bool] = None,
        evaluation_frequency: Optional[int] = None,
        gradient_accumulation_step: Optional[int] = None,
        layers_to_freeze: Optional[int] = None,
        learning_rate: Optional[float] = None,
        learning_rate_scheduler: Optional[Union[str, LearningRateScheduler]] = None,
        model_name: Optional[str] = None,
        momentum: Optional[float] = None,
        nesterov: Optional[bool] = None,
        number_of_epochs: Optional[int] = None,
        number_of_workers: Optional[int] = None,
        optimizer: Optional[Union[str, StochasticOptimizer]] = None,
        random_seed: Optional[int] = None,
        step_lr_gamma: Optional[float] = None,
        step_lr_step_size: Optional[int] = None,
        training_batch_size: Optional[int] = None,
        validation_batch_size: Optional[int] = None,
        warmup_cosine_lr_cycles: Optional[float] = None,
        warmup_cosine_lr_warmup_epochs: Optional[int] = None,
        weight_decay: Optional[float] = None,
        box_detections_per_image: Optional[int] = None,
        box_score_threshold: Optional[float] = None,
        image_size: Optional[int] = None,
        max_size: Optional[int] = None,
        min_size: Optional[int] = None,
        model_size: Optional[Union[str, ModelSize]] = None,
        multi_scale: Optional[bool] = None,
        nms_iou_threshold: Optional[float] = None,
        tile_grid_size: Optional[str] = None,
        tile_overlap_ratio: Optional[float] = None,
        tile_predictions_nms_threshold: Optional[float] = None,
        validation_iou_threshold: Optional[float] = None,
        validation_metric_type: Optional[Union[str, ValidationMetricType]] = None,
    ) -> None:
        """Setting Image training parameters for for AutoML Image Object Detection and Image Instance Segmentation
        tasks.

        :param advanced_settings: Settings for advanced scenarios.
        :type advanced_settings: str
        :param ams_gradient: Enable AMSGrad when optimizer is 'adam' or 'adamw'.
        :type ams_gradient: bool
        :param beta1: Value of 'beta1' when optimizer is 'adam' or 'adamw'. Must be a float in the
         range [0, 1].
        :type beta1: float
        :param beta2: Value of 'beta2' when optimizer is 'adam' or 'adamw'. Must be a float in the
         range [0, 1].
        :type beta2: float
        :param checkpoint_frequency: Frequency to store model checkpoints. Must be a positive
         integer.
        :type checkpoint_frequency: int
        :param checkpoint_run_id: The id of a previous run that has a pretrained checkpoint for
         incremental training.
        :type checkpoint_run_id: str
        :param distributed: Whether to use distributed training.
        :type distributed: bool
        :param early_stopping: Enable early stopping logic during training.
        :type early_stopping: bool
        :param early_stopping_delay: Minimum number of epochs or validation evaluations to wait
         before primary metric improvement
         is tracked for early stopping. Must be a positive integer.
        :type early_stopping_delay: int
        :param early_stopping_patience: Minimum number of epochs or validation evaluations with no
         primary metric improvement before
         the run is stopped. Must be a positive integer.
        :type early_stopping_patience: int
        :param enable_onnx_normalization: Enable normalization when exporting ONNX model.
        :type enable_onnx_normalization: bool
        :param evaluation_frequency: Frequency to evaluate validation dataset to get metric scores.
         Must be a positive integer.
        :type evaluation_frequency: int
        :param gradient_accumulation_step: Gradient accumulation means running a configured number of
         "GradAccumulationStep" steps without
         updating the model weights while accumulating the gradients of those steps, and then using
         the accumulated gradients to compute the weight updates. Must be a positive integer.
        :type gradient_accumulation_step: int
        :param layers_to_freeze: Number of layers to freeze for the model. Must be a positive
         integer.
         For instance, passing 2 as value for 'seresnext' means
         freezing layer0 and layer1. For a full list of models supported and details on layer freeze,
         please
         see: https://docs.microsoft.com/en-us/azure/machine-learning/reference-automl-images-hyperparameters#model-agnostic-hyperparameters.   # pylint: disable=line-too-long
        :type layers_to_freeze: int
        :param learning_rate: Initial learning rate. Must be a float in the range [0, 1].
        :type learning_rate: float
        :param learning_rate_scheduler: Type of learning rate scheduler. Must be 'warmup_cosine' or
         'step'. Possible values include: "None", "WarmupCosine", "Step".
        :type learning_rate_scheduler: str or
         ~azure.mgmt.machinelearningservices.models.LearningRateScheduler
        :param model_name: Name of the model to use for training.
         For more information on the available models please visit the official documentation:
         https://docs.microsoft.com/en-us/azure/machine-learning/how-to-auto-train-image-models.
        :type model_name: str
        :param momentum: Value of momentum when optimizer is 'sgd'. Must be a float in the range [0,
         1].
        :type momentum: float
        :param nesterov: Enable nesterov when optimizer is 'sgd'.
        :type nesterov: bool
        :param number_of_epochs: Number of training epochs. Must be a positive integer.
        :type number_of_epochs: int
        :param number_of_workers: Number of data loader workers. Must be a non-negative integer.
        :type number_of_workers: int
        :param optimizer: Type of optimizer. Possible values include: "None", "Sgd", "Adam", "Adamw".
        :type optimizer: str or ~azure.mgmt.machinelearningservices.models.StochasticOptimizer
        :param random_seed: Random seed to be used when using deterministic training.
        :type random_seed: int
        :param step_lr_gamma: Value of gamma when learning rate scheduler is 'step'. Must be a float
         in the range [0, 1].
        :type step_lr_gamma: float
        :param step_lr_step_size: Value of step size when learning rate scheduler is 'step'. Must be
         a positive integer.
        :type step_lr_step_size: int
        :param training_batch_size: Training batch size. Must be a positive integer.
        :type training_batch_size: int
        :param validation_batch_size: Validation batch size. Must be a positive integer.
        :type validation_batch_size: int
        :param warmup_cosine_lr_cycles: Value of cosine cycle when learning rate scheduler is
         'warmup_cosine'. Must be a float in the range [0, 1].
        :type warmup_cosine_lr_cycles: float
        :param warmup_cosine_lr_warmup_epochs: Value of warmup epochs when learning rate scheduler is
         'warmup_cosine'. Must be a positive integer.
        :type warmup_cosine_lr_warmup_epochs: int
        :param weight_decay: Value of weight decay when optimizer is 'sgd', 'adam', or 'adamw'. Must
         be a float in the range[0, 1].
        :type weight_decay: float
        :param box_detections_per_image: Maximum number of detections per image, for all classes.
         Must be a positive integer.
         Note: This settings is not supported for the 'yolov5' algorithm.
        :type box_detections_per_image: int
        :param box_score_threshold: During inference, only return proposals with a classification
         score greater than
         BoxScoreThreshold. Must be a float in the range[0, 1].
        :type box_score_threshold: float
        :param image_size: Image size for training and validation. Must be a positive integer.
         Note: The training run may get into CUDA OOM if the size is too big.
         Note: This settings is only supported for the 'yolov5' algorithm.
        :type image_size: int
        :param max_size: Maximum size of the image to be rescaled before feeding it to the backbone.
         Must be a positive integer. Note: training run may get into CUDA OOM if the size is too big.
         Note: This settings is not supported for the 'yolov5' algorithm.
        :type max_size: int
        :param min_size: Minimum size of the image to be rescaled before feeding it to the backbone.
         Must be a positive integer. Note: training run may get into CUDA OOM if the size is too big.
         Note: This settings is not supported for the 'yolov5' algorithm.
        :type min_size: int
        :param model_size: Model size. Must be 'small', 'medium', 'large', or 'extra_large'.
         Note: training run may get into CUDA OOM if the model size is too big.
         Note: This settings is only supported for the 'yolov5' algorithm.
        :type model_size: str or ~azure.mgmt.machinelearningservices.models.ModelSize
        :param multi_scale: Enable multi-scale image by varying image size by +/- 50%.
         Note: training run may get into CUDA OOM if no sufficient GPU memory.
         Note: This settings is only supported for the 'yolov5' algorithm.
        :type multi_scale: bool
        :param nms_iou_threshold: IOU threshold used during inference in NMS post processing. Must be
         float in the range [0, 1].
        :type nms_iou_threshold: float
        :param tile_grid_size: The grid size to use for tiling each image. Note: TileGridSize must
         not be
         None to enable small object detection logic. A string containing two integers in mxn format.
        :type tile_grid_size: str
        :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension. Must be
         float in the range [0, 1).
        :type tile_overlap_ratio: float
        :param tile_predictions_nms_threshold: The IOU threshold to use to perform NMS while merging
         predictions from tiles and image.
         Used in validation/ inference. Must be float in the range [0, 1].
         NMS: Non-maximum suppression.
        :type tile_predictions_nms_threshold: str
        :param validation_iou_threshold: IOU threshold to use when computing validation metric. Must
         be float in the range [0, 1].
        :type validation_iou_threshold: float
        :param validation_metric_type: Metric computation method to use for validation metrics. Must
         be 'none', 'coco', 'voc', or 'coco_voc'.
        :type validation_metric_type: str or ~azure.mgmt.machinelearningservices.models.ValidationMetricType
        """
        self._training_parameters = self._training_parameters or ImageModelSettingsObjectDetection()

        self._training_parameters.advanced_settings = (
            advanced_settings if advanced_settings is not None else self._training_parameters.advanced_settings
        )
        self._training_parameters.ams_gradient = (
            ams_gradient if ams_gradient is not None else self._training_parameters.ams_gradient
        )
        self._training_parameters.beta1 = beta1 if beta1 is not None else self._training_parameters.beta1
        self._training_parameters.beta2 = beta2 if beta2 is not None else self._training_parameters.beta2
        self._training_parameters.checkpoint_frequency = (
            checkpoint_frequency if checkpoint_frequency is not None else self._training_parameters.checkpoint_frequency
        )
        self._training_parameters.checkpoint_run_id = (
            checkpoint_run_id if checkpoint_run_id is not None else self._training_parameters.checkpoint_run_id
        )
        self._training_parameters.distributed = (
            distributed if distributed is not None else self._training_parameters.distributed
        )
        self._training_parameters.early_stopping = (
            early_stopping if early_stopping is not None else self._training_parameters.early_stopping
        )
        self._training_parameters.early_stopping_delay = (
            early_stopping_delay if early_stopping_delay is not None else self._training_parameters.early_stopping_delay
        )
        self._training_parameters.early_stopping_patience = (
            early_stopping_patience
            if early_stopping_patience is not None
            else self._training_parameters.early_stopping_patience
        )
        self._training_parameters.enable_onnx_normalization = (
            enable_onnx_normalization
            if enable_onnx_normalization is not None
            else self._training_parameters.enable_onnx_normalization
        )
        self._training_parameters.evaluation_frequency = (
            evaluation_frequency if evaluation_frequency is not None else self._training_parameters.evaluation_frequency
        )
        self._training_parameters.gradient_accumulation_step = (
            gradient_accumulation_step
            if gradient_accumulation_step is not None
            else self._training_parameters.gradient_accumulation_step
        )
        self._training_parameters.layers_to_freeze = (
            layers_to_freeze if layers_to_freeze is not None else self._training_parameters.layers_to_freeze
        )
        self._training_parameters.learning_rate = (
            learning_rate if learning_rate is not None else self._training_parameters.learning_rate
        )
        self._training_parameters.learning_rate_scheduler = (
            LearningRateScheduler[camel_to_snake(learning_rate_scheduler)]
            if learning_rate_scheduler is not None
            else self._training_parameters.learning_rate_scheduler
        )
        self._training_parameters.model_name = (
            model_name if model_name is not None else self._training_parameters.model_name
        )
        self._training_parameters.momentum = momentum if momentum is not None else self._training_parameters.momentum
        self._training_parameters.nesterov = nesterov if nesterov is not None else self._training_parameters.nesterov
        self._training_parameters.number_of_epochs = (
            number_of_epochs if number_of_epochs is not None else self._training_parameters.number_of_epochs
        )
        self._training_parameters.number_of_workers = (
            number_of_workers if number_of_workers is not None else self._training_parameters.number_of_workers
        )
        self._training_parameters.optimizer = (
            StochasticOptimizer[camel_to_snake(optimizer)]
            if optimizer is not None
            else self._training_parameters.optimizer
        )
        self._training_parameters.random_seed = (
            random_seed if random_seed is not None else self._training_parameters.random_seed
        )
        self._training_parameters.step_lr_gamma = (
            step_lr_gamma if step_lr_gamma is not None else self._training_parameters.step_lr_gamma
        )
        self._training_parameters.step_lr_step_size = (
            step_lr_step_size if step_lr_step_size is not None else self._training_parameters.step_lr_step_size
        )
        self._training_parameters.training_batch_size = (
            training_batch_size if training_batch_size is not None else self._training_parameters.training_batch_size
        )
        self._training_parameters.validation_batch_size = (
            validation_batch_size
            if validation_batch_size is not None
            else self._training_parameters.validation_batch_size
        )
        self._training_parameters.warmup_cosine_lr_cycles = (
            warmup_cosine_lr_cycles
            if warmup_cosine_lr_cycles is not None
            else self._training_parameters.warmup_cosine_lr_cycles
        )
        self._training_parameters.warmup_cosine_lr_warmup_epochs = (
            warmup_cosine_lr_warmup_epochs
            if warmup_cosine_lr_warmup_epochs is not None
            else self._training_parameters.warmup_cosine_lr_warmup_epochs
        )
        self._training_parameters.weight_decay = (
            weight_decay if weight_decay is not None else self._training_parameters.weight_decay
        )
        self._training_parameters.box_detections_per_image = (
            box_detections_per_image
            if box_detections_per_image is not None
            else self._training_parameters.box_detections_per_image
        )
        self._training_parameters.box_score_threshold = (
            box_score_threshold if box_score_threshold is not None else self._training_parameters.box_score_threshold
        )
        self._training_parameters.image_size = (
            image_size if image_size is not None else self._training_parameters.image_size
        )
        self._training_parameters.max_size = max_size if max_size is not None else self._training_parameters.max_size
        self._training_parameters.min_size = min_size if min_size is not None else self._training_parameters.min_size
        self._training_parameters.model_size = (
            ModelSize[camel_to_snake(model_size)] if model_size is not None else self._training_parameters.model_size
        )
        self._training_parameters.multi_scale = (
            multi_scale if multi_scale is not None else self._training_parameters.multi_scale
        )
        self._training_parameters.nms_iou_threshold = (
            nms_iou_threshold if nms_iou_threshold is not None else self._training_parameters.nms_iou_threshold
        )
        self._training_parameters.tile_grid_size = (
            tile_grid_size if tile_grid_size is not None else self._training_parameters.tile_grid_size
        )
        self._training_parameters.tile_overlap_ratio = (
            tile_overlap_ratio if tile_overlap_ratio is not None else self._training_parameters.tile_overlap_ratio
        )
        self._training_parameters.tile_predictions_nms_threshold = (
            tile_predictions_nms_threshold
            if tile_predictions_nms_threshold is not None
            else self._training_parameters.tile_predictions_nms_threshold
        )
        self._training_parameters.validation_iou_threshold = (
            validation_iou_threshold
            if validation_iou_threshold is not None
            else self._training_parameters.validation_iou_threshold
        )
        self._training_parameters.validation_metric_type = (
            ValidationMetricType[camel_to_snake(validation_metric_type)]
            if validation_metric_type is not None
            else self._training_parameters.validation_metric_type
        )

    # pylint: enable=too-many-locals

    def extend_search_space(
        self,
        value: Union[SearchSpace, List[SearchSpace]],
    ) -> None:
        """Add search space for AutoML Image Object Detection and Image Instance Segmentation tasks.

        :param value: Search through the parameter space
        :type value: Union[SearchSpace, List[SearchSpace]]
        """
        self._search_space = self._search_space or []

        if isinstance(value, list):
            self._search_space.extend(
                [cast_to_specific_search_space(item, ImageObjectDetectionSearchSpace, self.task_type) for item in value]
            )
        else:
            self._search_space.append(
                cast_to_specific_search_space(value, ImageObjectDetectionSearchSpace, self.task_type)
            )

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

        return self._training_parameters == other._training_parameters and self._search_space == other._search_space

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
