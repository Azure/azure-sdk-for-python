# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import Optional, Union

from azure.ai.ml import Input
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    LearningRateScheduler,
    ModelSize,
    StochasticOptimizer,
    ValidationMetricType,
)

from azure.ai.ml._restclient.v2022_10_01_preview.models import ImageModelSettingsClassification as RestImageModelSettingsClassification
from azure.ai.ml._restclient.v2022_10_01_preview.models import ImageModelSettingsObjectDetection as RestImageModelSettingsObjectDetection
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageModelDistributionSettings(RestTranslatableMixin):
    """Model settings for all AutoML Image Verticals.

    :param sampling_algorithm: Required. [Required] Type of the hyperparameter sampling
        algorithms. Possible values include: "Grid", "Random", "Bayesian".
    :type sampling_algorithm: Union[str, ~azure.mgmt.machinelearningservices.models.SamplingAlgorithmType.GRID,
    ~azure.mgmt.machinelearningservices.models.SamplingAlgorithmType.BAYESIAN,
    ~azure.mgmt.machinelearningservices.models.SamplingAlgorithmType.RANDOM]
    :param early_termination: Type of early termination policy.
    :type early_termination: Union[~azure.mgmt.machinelearningservices.models.BanditPolicy,
    ~azure.mgmt.machinelearningservices.models.MedianStoppingPolicy,
    ~azure.mgmt.machinelearningservices.models.TruncationSelectionPolicy]
    """

    def __init__(
        self,
        *,
        advanced_settings: str = None,
        ams_gradient: bool = None,
        augmentations: str = None,
        beta1: float = None,
        beta2: float = None,
        checkpoint_frequency: int = None,
        checkpoint_model: Input = None,
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
        learning_rate_scheduler: LearningRateScheduler = None,
        model_name: str = None,
        momentum: float = None,
        nesterov: bool = None,
        number_of_epochs: int = None,
        number_of_workers: int = None,
        optimizer: StochasticOptimizer = None,
        random_seed: int = None,
        step_lr_gamma: float = None,
        step_lr_step_size: int = None,
        training_batch_size: int = None,
        validation_batch_size: int = None,
        warmup_cosine_lr_cycles: float = None,
        warmup_cosine_lr_warmup_epochs: int = None,
        weight_decay: float = None,
    ):
        self.advanced_settings = advanced_settings
        self.ams_gradient = ams_gradient
        self.augmentations = augmentations
        self.beta1 = beta1
        self.beta2 = beta2
        self.checkpoint_frequency = checkpoint_frequency
        self.checkpoint_model = checkpoint_model
        self.checkpoint_run_id = checkpoint_run_id
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageModelDistributionSettings):
            return NotImplemented

        return (
            self.advanced_settings == other.advanced_settings
            and self.ams_gradient == other.ams_gradient
            and self.augmentations == other.augmentations
            and self.beta1 == other.beta1
            and self.beta2 == other.beta2
            and self.checkpoint_frequency == other.checkpoint_frequency
            and self.checkpoint_model == other.checkpoint_model
            and self.checkpoint_run_id == other.checkpoint_run_id
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
        )


class ImageModelSettingsClassification(ImageModelDistributionSettings):
    def __init__(
        self,
        *,
        advanced_settings: str = None,
        ams_gradient: bool = None,
        augmentations: str = None,
        beta1: float = None,
        beta2: float = None,
        checkpoint_frequency: int = None,
        checkpoint_model: Input = None,
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
        learning_rate_scheduler: LearningRateScheduler = None,
        model_name: str = None,
        momentum: float = None,
        nesterov: bool = None,
        number_of_epochs: int = None,
        number_of_workers: int = None,
        optimizer: StochasticOptimizer = None,
        random_seed: int = None,
        step_lr_gamma: float = None,
        step_lr_step_size: int = None,
        training_batch_size: int = None,
        validation_batch_size: int = None,
        warmup_cosine_lr_cycles: float = None,
        warmup_cosine_lr_warmup_epochs: int = None,
        weight_decay: float = None,
        training_crop_size: int = None,
        validation_crop_size: int = None,
        validation_resize_size: int = None,
        weighted_loss: int = None,
        **kwargs
    ):
        super(ImageModelSettingsClassification, self).__init__(advanced_settings=advanced_settings, ams_gradient=ams_gradient, augmentations=augmentations, beta1=beta1, beta2=beta2, checkpoint_frequency=checkpoint_frequency, checkpoint_model=checkpoint_model, checkpoint_run_id=checkpoint_run_id, distributed=distributed, early_stopping=early_stopping, early_stopping_delay=early_stopping_delay, early_stopping_patience=early_stopping_patience, enable_onnx_normalization=enable_onnx_normalization, evaluation_frequency=evaluation_frequency, gradient_accumulation_step=gradient_accumulation_step,
                                                               layers_to_freeze=layers_to_freeze, learning_rate=learning_rate, learning_rate_scheduler=learning_rate_scheduler, model_name=model_name, momentum=momentum, nesterov=nesterov, number_of_epochs=number_of_epochs, number_of_workers=number_of_workers, optimizer=optimizer, random_seed=random_seed, step_lr_gamma=step_lr_gamma, step_lr_step_size=step_lr_step_size, training_batch_size=training_batch_size, validation_batch_size=validation_batch_size, warmup_cosine_lr_cycles=warmup_cosine_lr_cycles, warmup_cosine_lr_warmup_epochs=warmup_cosine_lr_warmup_epochs, weight_decay=weight_decay, **kwargs)
        self.training_crop_size = training_crop_size
        self.validation_crop_size = validation_crop_size
        self.validation_resize_size = validation_resize_size
        self.weighted_loss = weighted_loss

    def _to_rest_object(self) -> RestImageModelSettingsClassification:
        return RestImageModelSettingsClassification(
            advanced_settings=self.advanced_settings,
            ams_gradient=self.ams_gradient,
            augmentations=self.augmentations,
            beta1=self.beta1,
            beta2=self.beta2,
            checkpoint_frequency=self.checkpoint_frequency,
            checkpoint_model=self.checkpoint_model,
            checkpoint_run_id=self.checkpoint_run_id,
            distributed=self.distributed,
            early_stopping=self.early_stopping,
            early_stopping_delay=self.early_stopping_delay,
            early_stopping_patience=self.early_stopping_patience,
            enable_onnx_normalization=self.enable_onnx_normalization,
            evaluation_frequency=self.evaluation_frequency,
            gradient_accumulation_step=self.gradient_accumulation_step,
            layers_to_freeze=self.layers_to_freeze,
            learning_rate=self.learning_rate,
            learning_rate_scheduler=self.learning_rate_scheduler,
            model_name=self.model_name,
            momentum=self.momentum,
            nesterov=self.nesterov,
            number_of_epochs=self.number_of_epochs,
            number_of_workers=self.number_of_workers,
            optimizer=self.optimizer,
            random_seed=self.random_seed,
            step_lr_gamma=self.step_lr_gamma,
            step_lr_step_size=self.step_lr_step_size,
            training_batch_size=self.training_batch_size,
            validation_batch_size=self.validation_batch_size,
            warmup_cosine_lr_cycles=self.warmup_cosine_lr_cycles,
            warmup_cosine_lr_warmup_epochs=self.warmup_cosine_lr_warmup_epochs,
            weight_decay=self.weight_decay,
            training_crop_size=self.training_crop_size,
            validation_crop_size=self.validation_crop_size,
            validation_resize_size=self.validation_resize_size,
            weighted_loss=self.weighted_loss
        )

    @classmethod
    def _from_rest_object(cls, obj: RestImageModelSettingsClassification) -> "ImageModelSettingsClassification":
        return cls(
            advanced_settings=obj.advanced_settings,
            ams_gradient=obj.ams_gradient,
            augmentations=obj.augmentations,
            beta1=obj.beta1,
            beta2=obj.beta2,
            checkpoint_frequency=obj.checkpoint_frequency,
            checkpoint_model=obj.checkpoint_model,
            checkpoint_run_id=obj.checkpoint_run_id,
            distributed=obj.distributed,
            early_stopping=obj.early_stopping,
            early_stopping_delay=obj.early_stopping_delay,
            early_stopping_patience=obj.early_stopping_patience,
            enable_onnx_normalization=obj.enable_onnx_normalization,
            evaluation_frequency=obj.evaluation_frequency,
            gradient_accumulation_step=obj.gradient_accumulation_step,
            layers_to_freeze=obj.layers_to_freeze,
            learning_rate=obj.learning_rate,
            learning_rate_scheduler=obj.learning_rate_scheduler,
            model_name=obj.model_name,
            momentum=obj.momentum,
            nesterov=obj.nesterov,
            number_of_epochs=obj.number_of_epochs,
            number_of_workers=obj.number_of_workers,
            optimizer=obj.optimizer,
            random_seed=obj.random_seed,
            step_lr_gamma=obj.step_lr_gamma,
            step_lr_step_size=obj.step_lr_step_size,
            training_batch_size=obj.training_batch_size,
            validation_batch_size=obj.validation_batch_size,
            warmup_cosine_lr_cycles=obj.warmup_cosine_lr_cycles,
            warmup_cosine_lr_warmup_epochs=obj.warmup_cosine_lr_warmup_epochs,
            weight_decay=obj.weight_decay,
            training_crop_size=obj.training_crop_size,
            validation_crop_size=obj.validation_crop_size,
            validation_resize_size=obj.validation_resize_size,
            weighted_loss=obj.weighted_loss
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageModelSettingsClassification):
            return NotImplemented

        return (
            super().__eq__(other)
            and self.training_crop_size == other.training_crop_size
            and self.validation_crop_size == other.validation_crop_size
            and self.validation_resize_size == other.validation_resize_size
            and self.weighted_loss == other.weighted_loss
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class ImageModelSettingsObjectDetection(ImageModelDistributionSettings):
    def __init__(
        self,
        *,
        advanced_settings: str = None,
        ams_gradient: bool = None,
        augmentations: str = None,
        beta1: float = None,
        beta2: float = None,
        checkpoint_frequency: int = None,
        checkpoint_model: Input = None,
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
        learning_rate_scheduler: LearningRateScheduler = None,
        model_name: str = None,
        momentum: float = None,
        nesterov: bool = None,
        number_of_epochs: int = None,
        number_of_workers: int = None,
        optimizer: StochasticOptimizer = None,
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
        model_size: ModelSize = None,
        multi_scale: bool = None,
        nms_iou_threshold: float = None,
        tile_grid_size: str = None,
        tile_overlap_ratio: float = None,
        tile_predictions_nms_threshold: float = None,
        validation_iou_threshold: float = None,
        validation_metric_type: ValidationMetricType = None,
        **kwargs
    ):
        super(ImageModelSettingsObjectDetection, self).__init__(advanced_settings=advanced_settings, ams_gradient=ams_gradient, augmentations=augmentations, beta1=beta1, beta2=beta2, checkpoint_frequency=checkpoint_frequency, checkpoint_model=checkpoint_model, checkpoint_run_id=checkpoint_run_id, distributed=distributed, early_stopping=early_stopping, early_stopping_delay=early_stopping_delay, early_stopping_patience=early_stopping_patience, enable_onnx_normalization=enable_onnx_normalization, evaluation_frequency=evaluation_frequency, gradient_accumulation_step=gradient_accumulation_step,
                                                                layers_to_freeze=layers_to_freeze, learning_rate=learning_rate, learning_rate_scheduler=learning_rate_scheduler, model_name=model_name, momentum=momentum, nesterov=nesterov, number_of_epochs=number_of_epochs, number_of_workers=number_of_workers, optimizer=optimizer, random_seed=random_seed, step_lr_gamma=step_lr_gamma, step_lr_step_size=step_lr_step_size, training_batch_size=training_batch_size, validation_batch_size=validation_batch_size, warmup_cosine_lr_cycles=warmup_cosine_lr_cycles, warmup_cosine_lr_warmup_epochs=warmup_cosine_lr_warmup_epochs, weight_decay=weight_decay, **kwargs)
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

    def _to_rest_object(self) -> RestImageModelSettingsObjectDetection:
        return RestImageModelSettingsObjectDetection(
            advanced_settings=self.advanced_settings,
            ams_gradient=self.ams_gradient,
            augmentations=self.augmentations,
            beta1=self.beta1,
            beta2=self.beta2,
            checkpoint_frequency=self.checkpoint_frequency,
            checkpoint_model=self.checkpoint_model,
            checkpoint_run_id=self.checkpoint_run_id,
            distributed=self.distributed,
            early_stopping=self.early_stopping,
            early_stopping_delay=self.early_stopping_delay,
            early_stopping_patience=self.early_stopping_patience,
            enable_onnx_normalization=self.enable_onnx_normalization,
            evaluation_frequency=self.evaluation_frequency,
            gradient_accumulation_step=self.gradient_accumulation_step,
            layers_to_freeze=self.layers_to_freeze,
            learning_rate=self.learning_rate,
            learning_rate_scheduler=self.learning_rate_scheduler,
            model_name=self.model_name,
            momentum=self.momentum,
            nesterov=self.nesterov,
            number_of_epochs=self.number_of_epochs,
            number_of_workers=self.number_of_workers,
            optimizer=self.optimizer,
            random_seed=self.random_seed,
            step_lr_gamma=self.step_lr_gamma,
            step_lr_step_size=self.step_lr_step_size,
            training_batch_size=self.training_batch_size,
            validation_batch_size=self.validation_batch_size,
            warmup_cosine_lr_cycles=self.warmup_cosine_lr_cycles,
            warmup_cosine_lr_warmup_epochs=self.warmup_cosine_lr_warmup_epochs,
            weight_decay=self.weight_decay,
            box_detections_per_image=self.box_detections_per_image,
            box_score_threshold=self.box_score_threshold,
            image_size=self.image_size,
            max_size=self.max_size,
            min_size=self.min_size,
            model_size=self.model_size,
            multi_scale=self.multi_scale,
            nms_iou_threshold=self.nms_iou_threshold,
            tile_grid_size=self.tile_grid_size,
            tile_overlap_ratio=self.tile_overlap_ratio,
            tile_predictions_nms_threshold=self.tile_predictions_nms_threshold,
            validation_iou_threshold=self.validation_iou_threshold,
            validation_metric_type=self.validation_metric_type
        )

    @classmethod
    def _from_rest_object(cls, obj: RestImageModelSettingsObjectDetection) -> "ImageModelSettingsObjectDetection":
        return cls(
            advanced_settings=obj.advanced_settings,
            ams_gradient=obj.ams_gradient,
            augmentations=obj.augmentations,
            beta1=obj.beta1,
            beta2=obj.beta2,
            checkpoint_frequency=obj.checkpoint_frequency,
            checkpoint_model=obj.checkpoint_model,
            checkpoint_run_id=obj.checkpoint_run_id,
            distributed=obj.distributed,
            early_stopping=obj.early_stopping,
            early_stopping_delay=obj.early_stopping_delay,
            early_stopping_patience=obj.early_stopping_patience,
            enable_onnx_normalization=obj.enable_onnx_normalization,
            evaluation_frequency=obj.evaluation_frequency,
            gradient_accumulation_step=obj.gradient_accumulation_step,
            layers_to_freeze=obj.layers_to_freeze,
            learning_rate=obj.learning_rate,
            learning_rate_scheduler=obj.learning_rate_scheduler,
            model_name=obj.model_name,
            momentum=obj.momentum,
            nesterov=obj.nesterov,
            number_of_epochs=obj.number_of_epochs,
            number_of_workers=obj.number_of_workers,
            optimizer=obj.optimizer,
            random_seed=obj.random_seed,
            step_lr_gamma=obj.step_lr_gamma,
            step_lr_step_size=obj.step_lr_step_size,
            training_batch_size=obj.training_batch_size,
            validation_batch_size=obj.validation_batch_size,
            warmup_cosine_lr_cycles=obj.warmup_cosine_lr_cycles,
            warmup_cosine_lr_warmup_epochs=obj.warmup_cosine_lr_warmup_epochs,
            weight_decay=obj.weight_decay,
            box_detections_per_image=obj.box_detections_per_image,
            box_score_threshold=obj.box_score_threshold,
            image_size=obj.image_size,
            max_size=obj.max_size,
            min_size=obj.min_size,
            model_size=obj.model_size,
            multi_scale=obj.multi_scale,
            nms_iou_threshold=obj.nms_iou_threshold,
            tile_grid_size=obj.tile_grid_size,
            tile_overlap_ratio=obj.tile_overlap_ratio,
            tile_predictions_nms_threshold=obj.tile_predictions_nms_threshold,
            validation_iou_threshold=obj.validation_iou_threshold,
            validation_metric_type=obj.validation_metric_type
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageModelSettingsObjectDetection):
            return NotImplemented

        return (
            super().__eq__(other)
            and self.box_detections_per_image == other.box_detections_per_image
            and self.box_score_threshold == other.box_score_threshold
            and self.image_size == other.image_size
            and self.max_size == other.max_size
            and self.min_size == other.min_size
            and self.model_size == other.model_size
            and self.multi_scale == other.multi_scale
            and self. nms_iou_threshold == other.nms_iou_threshold
            and self.tile_grid_size == other.tile_grid_size
            and self.tile_overlap_ratio == other.tile_overlap_ratio
            and self. tile_predictions_nms_threshold == other.tile_predictions_nms_threshold
            and self.validation_iou_threshold == other.validation_iou_threshold
            and self.validation_metric_type == other.validation_metric_type
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)