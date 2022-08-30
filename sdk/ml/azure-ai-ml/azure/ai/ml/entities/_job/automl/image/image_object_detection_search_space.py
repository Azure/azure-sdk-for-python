# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import ImageModelDistributionSettingsObjectDetection
from azure.ai.ml.entities._job.automl.image.image_search_space_utils import (
    _convert_from_rest_object,
    _convert_to_rest_object,
)
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageObjectDetectionSearchSpace(RestTranslatableMixin):
    """Search space for AutoML Image Object Detection and Image Instance
    Segmentation tasks.

    :param ams_gradient: Enable AMSGrad when optimizer is 'adam' or 'adamw'.
    :type ams_gradient: bool or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param augmentations: Settings for using Augmentations.
    :type augmentations: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param beta1: Value of 'beta1' when optimizer is 'adam' or 'adamw'. Must be a float in the
        range [0, 1].
    :type beta1: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param beta2: Value of 'beta2' when optimizer is 'adam' or 'adamw'. Must be a float in the
        range [0, 1].
    :type beta2: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param distributed: Whether to use distributer training.
    :type distributed: bool or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param early_stopping: Enable early stopping logic during training.
    :type early_stopping: bool or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param early_stopping_delay: Minimum number of epochs or validation evaluations to wait
        before primary metric improvement
        is tracked for early stopping. Must be a positive integer.
    :type early_stopping_delay: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param early_stopping_patience: Minimum number of epochs or validation evaluations with no
        primary metric improvement before
        the run is stopped. Must be a positive integer.
    :type early_stopping_patience: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param enable_onnx_normalization: Enable normalization when exporting ONNX model.
    :type enable_onnx_normalization: bool or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param evaluation_frequency: Frequency to evaluate validation dataset to get metric scores.
        Must be a positive integer.
    :type evaluation_frequency: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param gradient_accumulation_step: Gradient accumulation means running a configured number of
        "GradAccumulationStep" steps without
        updating the model weights while accumulating the gradients of those steps, and then using
        the accumulated gradients to compute the weight updates. Must be a positive integer.
    :type gradient_accumulation_step: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param layers_to_freeze: Number of layers to freeze for the model. Must be a positive
        integer.
        For instance, passing 2 as value for 'seresnext' means
        freezing layer0 and layer1. For a full list of models supported and details on layer freeze,
        please
        see: https://docs.microsoft.com/en-us/azure/machine-learning/reference-automl-images-hyperparameters#model-agnostic-hyperparameters.
    :type layers_to_freeze: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param learning_rate: Initial learning rate. Must be a float in the range [0, 1].
    :type learning_rate: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param learning_rate_scheduler: Type of learning rate scheduler. Must be 'warmup_cosine' or
        'step'.
    :type learning_rate_scheduler: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param model_name: Name of the model to use for training.
        For more information on the available models please visit the official documentation:
        https://docs.microsoft.com/en-us/azure/machine-learning/how-to-auto-train-image-models.
    :type model_name: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param momentum: Value of momentum when optimizer is 'sgd'. Must be a float in the range [0,
        1].
    :type momentum: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param nesterov: Enable nesterov when optimizer is 'sgd'.
    :type nesterov: bool or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param number_of_epochs: Number of training epochs. Must be a positive integer.
    :type number_of_epochs: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param number_of_workers: Number of data loader workers. Must be a non-negative integer.
    :type number_of_workers: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param optimizer: Type of optimizer. Must be either 'sgd', 'adam', or 'adamw'.
    :type optimizer: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param random_seed: Random seed to be used when using deterministic training.
    :type random_seed: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param step_lr_gamma: Value of gamma when learning rate scheduler is 'step'. Must be a float
        in the range [0, 1].
    :type step_lr_gamma: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param step_lr_step_size: Value of step size when learning rate scheduler is 'step'. Must be
        a positive integer.
    :type step_lr_step_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param training_batch_size: Training batch size. Must be a positive integer.
    :type training_batch_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param validation_batch_size: Validation batch size. Must be a positive integer.
    :type validation_batch_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param warmup_cosine_lr_cycles: Value of cosine cycle when learning rate scheduler is
        'warmup_cosine'. Must be a float in the range [0, 1].
    :type warmup_cosine_lr_cycles: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param warmup_cosine_lr_warmup_epochs: Value of warmup epochs when learning rate scheduler is
        'warmup_cosine'. Must be a positive integer.
    :type warmup_cosine_lr_warmup_epochs: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param weight_decay: Value of weight decay when optimizer is 'sgd', 'adam', or 'adamw'. Must
        be a float in the range[0, 1].
    :type weight_decay: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param box_detections_per_image: Maximum number of detections per image, for all classes.
        Must be a positive integer.
        Note: This settings is not supported for the 'yolov5' algorithm.
    :type box_detections_per_image: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param box_score_threshold: During inference, only return proposals with a classification
        score greater than
        BoxScoreThreshold. Must be a float in the range[0, 1].
    :type box_score_threshold: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param image_size: Image size for train and validation. Must be a positive integer.
        Note: The training run may get into CUDA OOM if the size is too big.
        Note: This settings is only supported for the 'yolov5' algorithm.
    :type image_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param max_size: Maximum size of the image to be rescaled before feeding it to the backbone.
        Must be a positive integer. Note: training run may get into CUDA OOM if the size is too big.
        Note: This settings is not supported for the 'yolov5' algorithm.
    :type max_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param min_size: Minimum size of the image to be rescaled before feeding it to the backbone.
        Must be a positive integer. Note: training run may get into CUDA OOM if the size is too big.
        Note: This settings is not supported for the 'yolov5' algorithm.
    :type min_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param model_size: Model size. Must be 'small', 'medium', 'large', or 'extra_large'.
        Note: training run may get into CUDA OOM if the model size is too big.
        Note: This settings is only supported for the 'yolov5' algorithm.
    :type model_size: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param multi_scale: Enable multi-scale image by varying image size by +/- 50%.
        Note: training run may get into CUDA OOM if no sufficient GPU memory.
        Note: This settings is only supported for the 'yolov5' algorithm.
    :type multi_scale: bool or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param nms_iou_threshold: IOU threshold used during inference in NMS post processing. Must be
        float in the range [0, 1].
    :type nms_iou_threshold: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param tile_grid_size: The grid size to use for tiling each image. Note: TileGridSize must
        not be
        None to enable small object detection logic. A string containing two integers in mxn format.
    :type tile_grid_size: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension. Must be
        float in the range [0, 1).
    :type tile_overlap_ratio: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param tile_predictions_nms_threshold: The IOU threshold to use to perform NMS while merging
        predictions from tiles and image.
        Used in validation/ inference. Must be float in the range [0, 1].
        NMS: Non-maximum suppression.
    :type tile_predictions_nms_threshold: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param validation_iou_threshold: IOU threshold to use when computing validation metric. Must
        be float in the range [0, 1].
    :type validation_iou_threshold: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param validation_metric_type: Metric computation method to use for validation metrics. Must
        be 'none', 'coco', 'voc', or 'coco_voc'.
    :type validation_metric_type: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    """

    def __init__(
        self,
        *,
        ams_gradient: Union[bool, SweepDistribution] = None,
        augmentations: Union[str, SweepDistribution] = None,
        beta1: Union[float, SweepDistribution] = None,
        beta2: Union[float, SweepDistribution] = None,
        distributed: Union[bool, SweepDistribution] = None,
        early_stopping: Union[bool, SweepDistribution] = None,
        early_stopping_delay: Union[int, SweepDistribution] = None,
        early_stopping_patience: Union[int, SweepDistribution] = None,
        enable_onnx_normalization: Union[bool, SweepDistribution] = None,
        evaluation_frequency: Union[int, SweepDistribution] = None,
        gradient_accumulation_step: Union[int, SweepDistribution] = None,
        layers_to_freeze: Union[int, SweepDistribution] = None,
        learning_rate: Union[float, SweepDistribution] = None,
        learning_rate_scheduler: Union[str, SweepDistribution] = None,
        model_name: Union[str, SweepDistribution] = None,
        momentum: Union[float, SweepDistribution] = None,
        nesterov: Union[bool, SweepDistribution] = None,
        number_of_epochs: Union[int, SweepDistribution] = None,
        number_of_workers: Union[int, SweepDistribution] = None,
        optimizer: Union[str, SweepDistribution] = None,
        random_seed: Union[int, SweepDistribution] = None,
        step_lr_gamma: Union[float, SweepDistribution] = None,
        step_lr_step_size: Union[int, SweepDistribution] = None,
        training_batch_size: Union[int, SweepDistribution] = None,
        validation_batch_size: Union[int, SweepDistribution] = None,
        warmup_cosine_lr_cycles: Union[float, SweepDistribution] = None,
        warmup_cosine_lr_warmup_epochs: Union[int, SweepDistribution] = None,
        weight_decay: Union[float, SweepDistribution] = None,
        box_detections_per_image: Union[int, SweepDistribution] = None,
        box_score_threshold: Union[float, SweepDistribution] = None,
        image_size: Union[int, SweepDistribution] = None,
        max_size: Union[int, SweepDistribution] = None,
        min_size: Union[int, SweepDistribution] = None,
        model_size: Union[str, SweepDistribution] = None,
        multi_scale: Union[bool, SweepDistribution] = None,
        nms_iou_threshold: Union[float, SweepDistribution] = None,
        tile_grid_size: Union[str, SweepDistribution] = None,
        tile_overlap_ratio: Union[float, SweepDistribution] = None,
        tile_predictions_nms_threshold: Union[float, SweepDistribution] = None,
        validation_iou_threshold: Union[float, SweepDistribution] = None,
        validation_metric_type: Union[str, SweepDistribution] = None,
    ) -> None:
        self.ams_gradient = ams_gradient
        self.augmentations = augmentations
        self.beta1 = beta1
        self.beta2 = beta2
        self.distributed = distributed
        self.early_stopping = early_stopping
        self.early_stopping_delay = early_stopping_delay
        self.early_stopping_patience = early_stopping_patience
        self.enable_onnx_normalization = enable_onnx_normalization
        self.evaluation_frequency = evaluation_frequency
        self.gradient_accumulation_step = gradient_accumulation_step
        self.layers_to_freeze = layers_to_freeze
        self.learning_rate = learning_rate
        self.learning_rate_scheduler = learning_rate_scheduler
        self.model_name = model_name
        self.momentum = momentum
        self.nesterov = nesterov
        self.number_of_epochs = number_of_epochs
        self.number_of_workers = number_of_workers
        self.optimizer = optimizer
        self.random_seed = random_seed
        self.step_lr_gamma = step_lr_gamma
        self.step_lr_step_size = step_lr_step_size
        self.training_batch_size = training_batch_size
        self.validation_batch_size = validation_batch_size
        self.warmup_cosine_lr_cycles = warmup_cosine_lr_cycles
        self.warmup_cosine_lr_warmup_epochs = warmup_cosine_lr_warmup_epochs
        self.weight_decay = weight_decay
        self.box_detections_per_image = box_detections_per_image
        self.box_score_threshold = box_score_threshold
        self.image_size = image_size
        self.max_size = max_size
        self.min_size = min_size
        self.model_size = model_size
        self.multi_scale = multi_scale
        self.nms_iou_threshold = nms_iou_threshold
        self.tile_grid_size = tile_grid_size
        self.tile_overlap_ratio = tile_overlap_ratio
        self.tile_predictions_nms_threshold = tile_predictions_nms_threshold
        self.validation_iou_threshold = validation_iou_threshold
        self.validation_metric_type = validation_metric_type

    def _to_rest_object(self) -> ImageModelDistributionSettingsObjectDetection:
        return ImageModelDistributionSettingsObjectDetection(
            ams_gradient=_convert_to_rest_object(self.ams_gradient) if self.ams_gradient is not None else None,
            augmentations=_convert_to_rest_object(self.augmentations) if self.augmentations is not None else None,
            beta1=_convert_to_rest_object(self.beta1) if self.beta1 is not None else None,
            beta2=_convert_to_rest_object(self.beta2) if self.beta2 is not None else None,
            distributed=_convert_to_rest_object(self.distributed) if self.distributed is not None else None,
            early_stopping=_convert_to_rest_object(self.early_stopping) if self.early_stopping is not None else None,
            early_stopping_delay=(
                _convert_to_rest_object(self.early_stopping_delay) if self.early_stopping_delay is not None else None
            ),
            early_stopping_patience=(
                _convert_to_rest_object(self.early_stopping_patience)
                if self.early_stopping_patience is not None
                else None
            ),
            enable_onnx_normalization=(
                _convert_to_rest_object(self.enable_onnx_normalization)
                if self.enable_onnx_normalization is not None
                else None
            ),
            evaluation_frequency=(
                _convert_to_rest_object(self.evaluation_frequency) if self.evaluation_frequency is not None else None
            ),
            gradient_accumulation_step=(
                _convert_to_rest_object(self.gradient_accumulation_step)
                if self.gradient_accumulation_step is not None
                else None
            ),
            layers_to_freeze=(
                _convert_to_rest_object(self.layers_to_freeze) if self.layers_to_freeze is not None else None
            ),
            learning_rate=_convert_to_rest_object(self.learning_rate) if self.learning_rate is not None else None,
            learning_rate_scheduler=(
                _convert_to_rest_object(self.learning_rate_scheduler)
                if self.learning_rate_scheduler is not None
                else None
            ),
            model_name=_convert_to_rest_object(self.model_name) if self.model_name is not None else None,
            momentum=_convert_to_rest_object(self.momentum) if self.momentum is not None else None,
            nesterov=_convert_to_rest_object(self.nesterov) if self.nesterov is not None else None,
            number_of_epochs=(
                _convert_to_rest_object(self.number_of_epochs) if self.number_of_epochs is not None else None
            ),
            number_of_workers=(
                _convert_to_rest_object(self.number_of_workers) if self.number_of_workers is not None else None
            ),
            optimizer=_convert_to_rest_object(self.optimizer) if self.optimizer is not None else None,
            random_seed=_convert_to_rest_object(self.random_seed) if self.random_seed is not None else None,
            step_lr_gamma=_convert_to_rest_object(self.step_lr_gamma) if self.step_lr_gamma is not None else None,
            step_lr_step_size=(
                _convert_to_rest_object(self.step_lr_step_size) if self.step_lr_step_size is not None else None
            ),
            training_batch_size=(
                _convert_to_rest_object(self.training_batch_size) if self.training_batch_size is not None else None
            ),
            validation_batch_size=(
                _convert_to_rest_object(self.validation_batch_size) if self.validation_batch_size is not None else None
            ),
            warmup_cosine_lr_cycles=(
                _convert_to_rest_object(self.warmup_cosine_lr_cycles)
                if self.warmup_cosine_lr_cycles is not None
                else None
            ),
            warmup_cosine_lr_warmup_epochs=(
                _convert_to_rest_object(self.warmup_cosine_lr_warmup_epochs)
                if self.warmup_cosine_lr_warmup_epochs is not None
                else None
            ),
            weight_decay=_convert_to_rest_object(self.weight_decay) if self.weight_decay is not None else None,
            box_detections_per_image=(
                _convert_to_rest_object(self.box_detections_per_image)
                if self.box_detections_per_image is not None
                else None
            ),
            box_score_threshold=(
                _convert_to_rest_object(self.box_score_threshold) if self.box_score_threshold is not None else None
            ),
            image_size=_convert_to_rest_object(self.image_size) if self.image_size is not None else None,
            max_size=_convert_to_rest_object(self.max_size) if self.max_size is not None else None,
            min_size=_convert_to_rest_object(self.min_size) if self.min_size is not None else None,
            model_size=_convert_to_rest_object(self.model_size) if self.model_size is not None else None,
            multi_scale=_convert_to_rest_object(self.multi_scale) if self.multi_scale is not None else None,
            nms_iou_threshold=(
                _convert_to_rest_object(self.nms_iou_threshold) if self.nms_iou_threshold is not None else None
            ),
            tile_grid_size=_convert_to_rest_object(self.tile_grid_size) if self.tile_grid_size is not None else None,
            tile_overlap_ratio=(
                _convert_to_rest_object(self.tile_overlap_ratio) if self.tile_overlap_ratio is not None else None
            ),
            tile_predictions_nms_threshold=(
                _convert_to_rest_object(self.tile_predictions_nms_threshold)
                if self.tile_predictions_nms_threshold is not None
                else None
            ),
            validation_iou_threshold=(
                _convert_to_rest_object(self.validation_iou_threshold)
                if self.validation_iou_threshold is not None
                else None
            ),
            validation_metric_type=(
                _convert_to_rest_object(self.validation_metric_type)
                if self.validation_metric_type is not None
                else None
            ),
        )

    @classmethod
    def _from_rest_object(cls, obj: ImageModelDistributionSettingsObjectDetection) -> "ImageObjectDetectionSearchSpace":
        return cls(
            ams_gradient=_convert_from_rest_object(obj.ams_gradient) if obj.ams_gradient is not None else None,
            augmentations=_convert_from_rest_object(obj.augmentations) if obj.augmentations is not None else None,
            beta1=_convert_from_rest_object(obj.beta1) if obj.beta1 is not None else None,
            beta2=_convert_from_rest_object(obj.beta2) if obj.beta2 is not None else None,
            distributed=_convert_from_rest_object(obj.distributed) if obj.distributed is not None else None,
            early_stopping=_convert_from_rest_object(obj.early_stopping) if obj.early_stopping is not None else None,
            early_stopping_delay=(
                _convert_from_rest_object(obj.early_stopping_delay) if obj.early_stopping_delay is not None else None
            ),
            early_stopping_patience=(
                _convert_from_rest_object(obj.early_stopping_patience)
                if obj.early_stopping_patience is not None
                else None
            ),
            enable_onnx_normalization=(
                _convert_from_rest_object(obj.enable_onnx_normalization)
                if obj.enable_onnx_normalization is not None
                else None
            ),
            evaluation_frequency=(
                _convert_from_rest_object(obj.evaluation_frequency) if obj.evaluation_frequency is not None else None
            ),
            gradient_accumulation_step=(
                _convert_from_rest_object(obj.gradient_accumulation_step)
                if obj.gradient_accumulation_step is not None
                else None
            ),
            layers_to_freeze=(
                _convert_from_rest_object(obj.layers_to_freeze) if obj.layers_to_freeze is not None else None
            ),
            learning_rate=_convert_from_rest_object(obj.learning_rate) if obj.learning_rate is not None else None,
            learning_rate_scheduler=(
                _convert_from_rest_object(obj.learning_rate_scheduler)
                if obj.learning_rate_scheduler is not None
                else None
            ),
            model_name=_convert_from_rest_object(obj.model_name) if obj.model_name is not None else None,
            momentum=_convert_from_rest_object(obj.momentum) if obj.momentum is not None else None,
            nesterov=_convert_from_rest_object(obj.nesterov) if obj.nesterov is not None else None,
            number_of_epochs=(
                _convert_from_rest_object(obj.number_of_epochs) if obj.number_of_epochs is not None else None
            ),
            number_of_workers=(
                _convert_from_rest_object(obj.number_of_workers) if obj.number_of_workers is not None else None
            ),
            optimizer=_convert_from_rest_object(obj.optimizer) if obj.optimizer is not None else None,
            random_seed=_convert_from_rest_object(obj.random_seed) if obj.random_seed is not None else None,
            step_lr_gamma=_convert_from_rest_object(obj.step_lr_gamma) if obj.step_lr_gamma is not None else None,
            step_lr_step_size=(
                _convert_from_rest_object(obj.step_lr_step_size) if obj.step_lr_step_size is not None else None
            ),
            training_batch_size=(
                _convert_from_rest_object(obj.training_batch_size) if obj.training_batch_size is not None else None
            ),
            validation_batch_size=(
                _convert_from_rest_object(obj.validation_batch_size) if obj.validation_batch_size is not None else None
            ),
            warmup_cosine_lr_cycles=(
                _convert_from_rest_object(obj.warmup_cosine_lr_cycles)
                if obj.warmup_cosine_lr_cycles is not None
                else None
            ),
            warmup_cosine_lr_warmup_epochs=(
                _convert_from_rest_object(obj.warmup_cosine_lr_warmup_epochs)
                if obj.warmup_cosine_lr_warmup_epochs is not None
                else None
            ),
            weight_decay=_convert_from_rest_object(obj.weight_decay) if obj.weight_decay is not None else None,
            box_detections_per_image=(
                _convert_from_rest_object(obj.box_detections_per_image)
                if obj.box_detections_per_image is not None
                else None
            ),
            box_score_threshold=(
                _convert_from_rest_object(obj.box_score_threshold) if obj.box_score_threshold is not None else None
            ),
            image_size=_convert_from_rest_object(obj.image_size) if obj.image_size is not None else None,
            max_size=_convert_from_rest_object(obj.max_size) if obj.max_size is not None else None,
            min_size=_convert_from_rest_object(obj.min_size) if obj.min_size is not None else None,
            model_size=_convert_from_rest_object(obj.model_size) if obj.model_size is not None else None,
            multi_scale=_convert_from_rest_object(obj.multi_scale) if obj.multi_scale is not None else None,
            nms_iou_threshold=(
                _convert_from_rest_object(obj.nms_iou_threshold) if obj.nms_iou_threshold is not None else None
            ),
            tile_grid_size=_convert_from_rest_object(obj.tile_grid_size) if obj.tile_grid_size is not None else None,
            tile_overlap_ratio=(
                _convert_from_rest_object(obj.tile_overlap_ratio) if obj.tile_overlap_ratio is not None else None
            ),
            tile_predictions_nms_threshold=(
                _convert_from_rest_object(obj.tile_predictions_nms_threshold)
                if obj.tile_predictions_nms_threshold is not None
                else None
            ),
            validation_iou_threshold=(
                _convert_from_rest_object(obj.validation_iou_threshold)
                if obj.validation_iou_threshold is not None
                else None
            ),
            validation_metric_type=(
                _convert_from_rest_object(obj.validation_metric_type)
                if obj.validation_metric_type is not None
                else None
            ),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageObjectDetectionSearchSpace):
            return NotImplemented

        return (
            self.ams_gradient == other.ams_gradient
            and self.augmentations == other.augmentations
            and self.beta1 == other.beta1
            and self.beta2 == other.beta2
            and self.distributed == other.distributed
            and self.early_stopping == other.early_stopping
            and self.early_stopping_delay == other.early_stopping_delay
            and self.early_stopping_patience == other.early_stopping_patience
            and self.enable_onnx_normalization == other.enable_onnx_normalization
            and self.evaluation_frequency == other.evaluation_frequency
            and self.gradient_accumulation_step == other.gradient_accumulation_step
            and self.layers_to_freeze == other.layers_to_freeze
            and self.learning_rate == other.learning_rate
            and self.learning_rate_scheduler == other.learning_rate_scheduler
            and self.model_name == other.model_name
            and self.momentum == other.momentum
            and self.nesterov == other.nesterov
            and self.number_of_epochs == other.number_of_epochs
            and self.number_of_workers == other.number_of_workers
            and self.optimizer == other.optimizer
            and self.random_seed == other.random_seed
            and self.step_lr_gamma == other.step_lr_gamma
            and self.step_lr_step_size == other.step_lr_step_size
            and self.training_batch_size == other.training_batch_size
            and self.validation_batch_size == other.validation_batch_size
            and self.warmup_cosine_lr_cycles == other.warmup_cosine_lr_cycles
            and self.warmup_cosine_lr_warmup_epochs == other.warmup_cosine_lr_warmup_epochs
            and self.weight_decay == other.weight_decay
            and self.box_detections_per_image == other.box_detections_per_image
            and self.box_score_threshold == other.box_score_threshold
            and self.image_size == other.image_size
            and self.max_size == other.max_size
            and self.min_size == other.min_size
            and self.model_size == other.model_size
            and self.multi_scale == other.multi_scale
            and self.nms_iou_threshold == other.nms_iou_threshold
            and self.tile_grid_size == other.tile_grid_size
            and self.tile_overlap_ratio == other.tile_overlap_ratio
            and self.tile_predictions_nms_threshold == other.tile_predictions_nms_threshold
            and self.validation_iou_threshold == other.validation_iou_threshold
            and self.validation_metric_type == other.validation_metric_type
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
