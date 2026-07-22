# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Optional

# pylint: disable=R0902,too-many-locals
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ImageModelSettingsClassification as RestImageModelSettingsClassification,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ImageModelSettingsObjectDetection as RestImageModelSettingsObjectDetection,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    LearningRateScheduler,
    LogTrainingMetrics,
    LogValidationLoss,
    ModelSize,
    StochasticOptimizer,
    ValidationMetricType,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageModelDistributionSettings(RestTranslatableMixin):
    """Model settings for all AutoML Image Verticals.
    Please do not instantiate directly. Use the child classes instead.

    :keyword advanced_settings: Settings for advanced scenarios.
    :paramtype advanced_settings: str
    :keyword ams_gradient: Enable AMSGrad when optimizer is 'adam' or 'adamw'.
    :paramtype ams_gradient: bool
    :keyword beta1: Value of 'beta1' when optimizer is 'adam' or 'adamw'. Must be a float in the range
     [0, 1].
    :paramtype beta1: float
    :keyword beta2: Value of 'beta2' when optimizer is 'adam' or 'adamw'. Must be a float in the range
     [0, 1].
    :paramtype beta2: float
    :keyword checkpoint_frequency: Frequency to store model checkpoints. Must be a positive integer.
    :paramtype checkpoint_frequency: int
    :keyword checkpoint_run_id: The id of a previous run that has a pretrained checkpoint for
     incremental training.
    :paramtype checkpoint_run_id: str
    :keyword distributed: Whether to use distributed training.
    :paramtype distributed: bool
    :keyword early_stopping: Enable early stopping logic during training.
    :paramtype early_stopping: bool
    :keyword early_stopping_delay: Minimum number of epochs or validation evaluations to wait before
     primary metric improvement
     is tracked for early stopping. Must be a positive integer.
    :paramtype early_stopping_delay: int
    :keyword early_stopping_patience: Minimum number of epochs or validation evaluations with no
     primary metric improvement before
     the run is stopped. Must be a positive integer.
    :paramtype early_stopping_patience: int
    :keyword enable_onnx_normalization: Enable normalization when exporting ONNX model.
    :paramtype enable_onnx_normalization: bool
    :keyword evaluation_frequency: Frequency to evaluate validation dataset to get metric scores. Must
     be a positive integer.
    :paramtype evaluation_frequency: int
    :keyword gradient_accumulation_step: Gradient accumulation means running a configured number of
     "GradAccumulationStep" steps without
     updating the model weights while accumulating the gradients of those steps, and then using
     the accumulated gradients to compute the weight updates. Must be a positive integer.
    :paramtype gradient_accumulation_step: int
    :keyword layers_to_freeze: Number of layers to freeze for the model. Must be a positive integer.
     For instance, passing 2 as value for 'seresnext' means
     freezing layer0 and layer1. For a full list of models supported and details on layer freeze,
     please
     see: https://learn.microsoft.com/azure/machine-learning/how-to-auto-train-image-models.
    :paramtype layers_to_freeze: int
    :keyword learning_rate: Initial learning rate. Must be a float in the range [0, 1].
    :paramtype learning_rate: float
    :keyword learning_rate_scheduler: Type of learning rate scheduler. Must be 'warmup_cosine' or
     'step'. Possible values include: "None", "WarmupCosine", "Step".
    :paramtype learning_rate_scheduler: str or
     ~azure.mgmt.machinelearningservices.models.LearningRateScheduler
    :keyword model_name: Name of the model to use for training.
     For more information on the available models please visit the official documentation:
     https://learn.microsoft.com/azure/machine-learning/how-to-auto-train-image-models.
    :paramtype model_name: str
    :keyword momentum: Value of momentum when optimizer is 'sgd'. Must be a float in the range [0, 1].
    :paramtype momentum: float
    :keyword nesterov: Enable nesterov when optimizer is 'sgd'.
    :paramtype nesterov: bool
    :keyword number_of_epochs: Number of training epochs. Must be a positive integer.
    :paramtype number_of_epochs: int
    :keyword number_of_workers: Number of data loader workers. Must be a non-negative integer.
    :paramtype number_of_workers: int
    :keyword optimizer: Type of optimizer. Possible values include: "None", "Sgd", "Adam", "Adamw".
    :paramtype optimizer: str or ~azure.mgmt.machinelearningservices.models.StochasticOptimizer
    :keyword random_seed: Random seed to be used when using deterministic training.
    :paramtype random_seed: int
    :keyword step_lr_gamma: Value of gamma when learning rate scheduler is 'step'. Must be a float in
     the range [0, 1].
    :paramtype step_lr_gamma: float
    :keyword step_lr_step_size: Value of step size when learning rate scheduler is 'step'. Must be a
     positive integer.
    :paramtype step_lr_step_size: int
    :keyword training_batch_size: Training batch size. Must be a positive integer.
    :paramtype training_batch_size: int
    :keyword validation_batch_size: Validation batch size. Must be a positive integer.
    :paramtype validation_batch_size: int
    :keyword warmup_cosine_lr_cycles: Value of cosine cycle when learning rate scheduler is
     'warmup_cosine'. Must be a float in the range [0, 1].
    :paramtype warmup_cosine_lr_cycles: float
    :keyword warmup_cosine_lr_warmup_epochs: Value of warmup epochs when learning rate scheduler is
     'warmup_cosine'. Must be a positive integer.
    :paramtype warmup_cosine_lr_warmup_epochs: int
    :keyword weight_decay: Value of weight decay when optimizer is 'sgd', 'adam', or 'adamw'. Must be
     a float in the range[0, 1].
    :paramtype weight_decay: float
    """

    def __init__(
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
        learning_rate_scheduler: Optional[LearningRateScheduler] = None,
        model_name: Optional[str] = None,
        momentum: Optional[float] = None,
        nesterov: Optional[bool] = None,
        number_of_epochs: Optional[int] = None,
        number_of_workers: Optional[int] = None,
        optimizer: Optional[StochasticOptimizer] = None,
        random_seed: Optional[int] = None,
        step_lr_gamma: Optional[float] = None,
        step_lr_step_size: Optional[int] = None,
        training_batch_size: Optional[int] = None,
        validation_batch_size: Optional[int] = None,
        warmup_cosine_lr_cycles: Optional[float] = None,
        warmup_cosine_lr_warmup_epochs: Optional[int] = None,
        weight_decay: Optional[float] = None,
    ):
        self.advanced_settings = advanced_settings
        self.ams_gradient = ams_gradient
        self.beta1 = beta1
        self.beta2 = beta2
        self.checkpoint_frequency = checkpoint_frequency
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
            and self.beta1 == other.beta1
            and self.beta2 == other.beta2
            and self.checkpoint_frequency == other.checkpoint_frequency
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
    """Model settings for AutoML Image Classification tasks.

    :keyword advanced_settings: Settings for advanced scenarios.
    :paramtype advanced_settings: str
    :keyword ams_gradient: Enable AMSGrad when optimizer is 'adam' or 'adamw'.
    :paramtype ams_gradient: bool
    :keyword beta1: Value of 'beta1' when optimizer is 'adam' or 'adamw'. Must be a float in the range
     [0, 1].
    :paramtype beta1: float
    :keyword beta2: Value of 'beta2' when optimizer is 'adam' or 'adamw'. Must be a float in the range
     [0, 1].
    :paramtype beta2: float
    :keyword checkpoint_frequency: Frequency to store model checkpoints. Must be a positive integer.
    :paramtype checkpoint_frequency: int
    :keyword checkpoint_run_id: The id of a previous run that has a pretrained checkpoint for
     incremental training.
    :paramtype checkpoint_run_id: str
    :keyword distributed: Whether to use distributed training.
    :paramtype distributed: bool
    :keyword early_stopping: Enable early stopping logic during training.
    :paramtype early_stopping: bool
    :keyword early_stopping_delay: Minimum number of epochs or validation evaluations to wait before
     primary metric improvement
     is tracked for early stopping. Must be a positive integer.
    :paramtype early_stopping_delay: int
    :keyword early_stopping_patience: Minimum number of epochs or validation evaluations with no
     primary metric improvement before
     the run is stopped. Must be a positive integer.
    :paramtype early_stopping_patience: int
    :keyword enable_onnx_normalization: Enable normalization when exporting ONNX model.
    :paramtype enable_onnx_normalization: bool
    :keyword evaluation_frequency: Frequency to evaluate validation dataset to get metric scores. Must
     be a positive integer.
    :paramtype evaluation_frequency: int
    :keyword gradient_accumulation_step: Gradient accumulation means running a configured number of
     "GradAccumulationStep" steps without
     updating the model weights while accumulating the gradients of those steps, and then using
     the accumulated gradients to compute the weight updates. Must be a positive integer.
    :paramtype gradient_accumulation_step: int
    :keyword layers_to_freeze: Number of layers to freeze for the model. Must be a positive integer.
     For instance, passing 2 as value for 'seresnext' means
     freezing layer0 and layer1. For a full list of models supported and details on layer freeze,
     please
     see: https://learn.microsoft.com/azure/machine-learning/how-to-auto-train-image-models.
    :paramtype layers_to_freeze: int
    :keyword learning_rate: Initial learning rate. Must be a float in the range [0, 1].
    :paramtype learning_rate: float
    :keyword learning_rate_scheduler: Type of learning rate scheduler. Must be 'warmup_cosine' or
     'step'. Possible values include: "None", "WarmupCosine", "Step".
    :paramtype learning_rate_scheduler: str or
     ~azure.mgmt.machinelearningservices.models.LearningRateScheduler
    :keyword model_name: Name of the model to use for training.
     For more information on the available models please visit the official documentation:
     https://learn.microsoft.com/azure/machine-learning/how-to-auto-train-image-models.
    :paramtype model_name: str
    :keyword momentum: Value of momentum when optimizer is 'sgd'. Must be a float in the range [0, 1].
    :paramtype momentum: float
    :keyword nesterov: Enable nesterov when optimizer is 'sgd'.
    :paramtype nesterov: bool
    :keyword number_of_epochs: Number of training epochs. Must be a positive integer.
    :paramtype number_of_epochs: int
    :keyword number_of_workers: Number of data loader workers. Must be a non-negative integer.
    :paramtype number_of_workers: int
    :keyword optimizer: Type of optimizer. Possible values include: "None", "Sgd", "Adam", "Adamw".
    :paramtype optimizer: str or ~azure.mgmt.machinelearningservices.models.StochasticOptimizer
    :keyword random_seed: Random seed to be used when using deterministic training.
    :paramtype random_seed: int
    :keyword step_lr_gamma: Value of gamma when learning rate scheduler is 'step'. Must be a float in
     the range [0, 1].
    :paramtype step_lr_gamma: float
    :keyword step_lr_step_size: Value of step size when learning rate scheduler is 'step'. Must be a
     positive integer.
    :paramtype step_lr_step_size: int
    :keyword training_batch_size: Training batch size. Must be a positive integer.
    :paramtype training_batch_size: int
    :keyword validation_batch_size: Validation batch size. Must be a positive integer.
    :paramtype validation_batch_size: int
    :keyword warmup_cosine_lr_cycles: Value of cosine cycle when learning rate scheduler is
     'warmup_cosine'. Must be a float in the range [0, 1].
    :paramtype warmup_cosine_lr_cycles: float
    :keyword warmup_cosine_lr_warmup_epochs: Value of warmup epochs when learning rate scheduler is
     'warmup_cosine'. Must be a positive integer.
    :paramtype warmup_cosine_lr_warmup_epochs: int
    :keyword weight_decay: Value of weight decay when optimizer is 'sgd', 'adam', or 'adamw'. Must be
     a float in the range[0, 1].
    :paramtype weight_decay: float
    :keyword training_crop_size: Image crop size that is input to the neural network for the training
     dataset. Must be a positive integer.
    :paramtype training_crop_size: int
    :keyword validation_crop_size: Image crop size that is input to the neural network for the
     validation dataset. Must be a positive integer.
    :paramtype validation_crop_size: int
    :keyword validation_resize_size: Image size to which to resize before cropping for validation
     dataset. Must be a positive integer.
    :paramtype validation_resize_size: int
    :keyword weighted_loss: Weighted loss. The accepted values are 0 for no weighted loss.
     1 for weighted loss with sqrt.(class_weights). 2 for weighted loss with class_weights. Must be
     0 or 1 or 2.
    :paramtype weighted_loss: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_image.py
            :start-after: [START automl.automl_image_job.image_classification_model_settings]
            :end-before: [END automl.automl_image_job.image_classification_model_settings]
            :language: python
            :dedent: 8
            :caption: Defining the automl image classification model settings.
    """

    def __init__(
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
        learning_rate_scheduler: Optional[LearningRateScheduler] = None,
        model_name: Optional[str] = None,
        momentum: Optional[float] = None,
        nesterov: Optional[bool] = None,
        number_of_epochs: Optional[int] = None,
        number_of_workers: Optional[int] = None,
        optimizer: Optional[StochasticOptimizer] = None,
        random_seed: Optional[int] = None,
        step_lr_gamma: Optional[float] = None,
        step_lr_step_size: Optional[int] = None,
        training_batch_size: Optional[int] = None,
        validation_batch_size: Optional[int] = None,
        warmup_cosine_lr_cycles: Optional[float] = None,
        warmup_cosine_lr_warmup_epochs: Optional[int] = None,
        weight_decay: Optional[float] = None,
        training_crop_size: Optional[int] = None,
        validation_crop_size: Optional[int] = None,
        validation_resize_size: Optional[int] = None,
        weighted_loss: Optional[int] = None,
        **kwargs: Any,
    ):
        super(ImageModelSettingsClassification, self).__init__(
            advanced_settings=advanced_settings,
            ams_gradient=ams_gradient,
            beta1=beta1,
            beta2=beta2,
            checkpoint_frequency=checkpoint_frequency,
            checkpoint_run_id=checkpoint_run_id,
            distributed=distributed,
            early_stopping=early_stopping,
            early_stopping_delay=early_stopping_delay,
            early_stopping_patience=early_stopping_patience,
            enable_onnx_normalization=enable_onnx_normalization,
            evaluation_frequency=evaluation_frequency,
            gradient_accumulation_step=gradient_accumulation_step,
            layers_to_freeze=layers_to_freeze,
            learning_rate=learning_rate,
            learning_rate_scheduler=learning_rate_scheduler,
            model_name=model_name,
            momentum=momentum,
            nesterov=nesterov,
            number_of_epochs=number_of_epochs,
            number_of_workers=number_of_workers,
            optimizer=optimizer,
            random_seed=random_seed,
            step_lr_gamma=step_lr_gamma,
            step_lr_step_size=step_lr_step_size,
            training_batch_size=training_batch_size,
            validation_batch_size=validation_batch_size,
            warmup_cosine_lr_cycles=warmup_cosine_lr_cycles,
            warmup_cosine_lr_warmup_epochs=warmup_cosine_lr_warmup_epochs,
            weight_decay=weight_decay,
            **kwargs,
        )
        self.training_crop_size = training_crop_size
        self.validation_crop_size = validation_crop_size
        self.validation_resize_size = validation_resize_size
        self.weighted_loss = weighted_loss

    def _to_rest_object(self) -> RestImageModelSettingsClassification:
        return RestImageModelSettingsClassification(
            advanced_settings=self.advanced_settings,
            ams_gradient=self.ams_gradient,
            beta1=self.beta1,
            beta2=self.beta2,
            checkpoint_frequency=self.checkpoint_frequency,
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
            weighted_loss=self.weighted_loss,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestImageModelSettingsClassification) -> "ImageModelSettingsClassification":
        return cls(
            advanced_settings=obj.advanced_settings,
            ams_gradient=obj.ams_gradient,
            beta1=obj.beta1,
            beta2=obj.beta2,
            checkpoint_frequency=obj.checkpoint_frequency,
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
            weighted_loss=obj.weighted_loss,
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
    """Model settings for AutoML Image Object Detection Task.

    :keyword advanced_settings: Settings for advanced scenarios.
    :paramtype advanced_settings: str
    :keyword ams_gradient: Enable AMSGrad when optimizer is 'adam' or 'adamw'.
    :paramtype ams_gradient: bool
    :keyword beta1: Value of 'beta1' when optimizer is 'adam' or 'adamw'. Must be a float in the range
     [0, 1].
    :paramtype beta1: float
    :keyword beta2: Value of 'beta2' when optimizer is 'adam' or 'adamw'. Must be a float in the range
     [0, 1].
    :paramtype beta2: float
    :keyword checkpoint_frequency: Frequency to store model checkpoints. Must be a positive integer.
    :paramtype checkpoint_frequency: int
    :keyword checkpoint_run_id: The id of a previous run that has a pretrained checkpoint for
     incremental training.
    :paramtype checkpoint_run_id: str
    :keyword distributed: Whether to use distributed training.
    :paramtype distributed: bool
    :keyword early_stopping: Enable early stopping logic during training.
    :paramtype early_stopping: bool
    :keyword early_stopping_delay: Minimum number of epochs or validation evaluations to wait before
     primary metric improvement
     is tracked for early stopping. Must be a positive integer.
    :paramtype early_stopping_delay: int
    :keyword early_stopping_patience: Minimum number of epochs or validation evaluations with no
     primary metric improvement before
     the run is stopped. Must be a positive integer.
    :paramtype early_stopping_patience: int
    :keyword enable_onnx_normalization: Enable normalization when exporting ONNX model.
    :paramtype enable_onnx_normalization: bool
    :keyword evaluation_frequency: Frequency to evaluate validation dataset to get metric scores. Must
     be a positive integer.
    :paramtype evaluation_frequency: int
    :keyword gradient_accumulation_step: Gradient accumulation means running a configured number of
     "GradAccumulationStep" steps without
     updating the model weights while accumulating the gradients of those steps, and then using
     the accumulated gradients to compute the weight updates. Must be a positive integer.
    :paramtype gradient_accumulation_step: int
    :keyword layers_to_freeze: Number of layers to freeze for the model. Must be a positive integer.
     For instance, passing 2 as value for 'seresnext' means
     freezing layer0 and layer1. For a full list of models supported and details on layer freeze,
     please
     see: https://learn.microsoft.com/azure/machine-learning/how-to-auto-train-image-models.
    :paramtype layers_to_freeze: int
    :keyword learning_rate: Initial learning rate. Must be a float in the range [0, 1].
    :paramtype learning_rate: float
    :keyword learning_rate_scheduler: Type of learning rate scheduler. Must be 'warmup_cosine' or
     'step'. Possible values include: "None", "WarmupCosine", "Step".
    :paramtype learning_rate_scheduler: str or
     ~azure.mgmt.machinelearningservices.models.LearningRateScheduler
    :keyword model_name: Name of the model to use for training.
     For more information on the available models please visit the official documentation:
     https://learn.microsoft.com/azure/machine-learning/how-to-auto-train-image-models.
    :paramtype model_name: str
    :keyword momentum: Value of momentum when optimizer is 'sgd'. Must be a float in the range [0, 1].
    :paramtype momentum: float
    :keyword nesterov: Enable nesterov when optimizer is 'sgd'.
    :paramtype nesterov: bool
    :keyword number_of_epochs: Number of training epochs. Must be a positive integer.
    :paramtype number_of_epochs: int
    :keyword number_of_workers: Number of data loader workers. Must be a non-negative integer.
    :paramtype number_of_workers: int
    :keyword optimizer: Type of optimizer. Possible values include: "None", "Sgd", "Adam", "Adamw".
    :paramtype optimizer: str or ~azure.mgmt.machinelearningservices.models.StochasticOptimizer
    :keyword random_seed: Random seed to be used when using deterministic training.
    :paramtype random_seed: int
    :keyword step_lr_gamma: Value of gamma when learning rate scheduler is 'step'. Must be a float in
     the range [0, 1].
    :paramtype step_lr_gamma: float
    :keyword step_lr_step_size: Value of step size when learning rate scheduler is 'step'. Must be a
     positive integer.
    :paramtype step_lr_step_size: int
    :keyword training_batch_size: Training batch size. Must be a positive integer.
    :paramtype training_batch_size: int
    :keyword validation_batch_size: Validation batch size. Must be a positive integer.
    :paramtype validation_batch_size: int
    :keyword warmup_cosine_lr_cycles: Value of cosine cycle when learning rate scheduler is
     'warmup_cosine'. Must be a float in the range [0, 1].
    :paramtype warmup_cosine_lr_cycles: float
    :keyword warmup_cosine_lr_warmup_epochs: Value of warmup epochs when learning rate scheduler is
     'warmup_cosine'. Must be a positive integer.
    :paramtype warmup_cosine_lr_warmup_epochs: int
    :keyword weight_decay: Value of weight decay when optimizer is 'sgd', 'adam', or 'adamw'. Must be
     a float in the range[0, 1].
    :paramtype weight_decay: float
    :keyword box_detections_per_image: Maximum number of detections per image, for all classes. Must
     be a positive integer.
     Note: This settings is not supported for the 'yolov5' algorithm.
    :paramtype box_detections_per_image: int
    :keyword box_score_threshold: During inference, only return proposals with a classification score
     greater than
     BoxScoreThreshold. Must be a float in the range[0, 1].
    :paramtype box_score_threshold: float
    :keyword image_size: Image size for train and validation. Must be a positive integer.
     Note: The training run may get into CUDA OOM if the size is too big.
     Note: This settings is only supported for the 'yolov5' algorithm.
    :paramtype image_size: int
    :keyword max_size: Maximum size of the image to be rescaled before feeding it to the backbone.
     Must be a positive integer. Note: training run may get into CUDA OOM if the size is too big.
     Note: This settings is not supported for the 'yolov5' algorithm.
    :paramtype max_size: int
    :keyword min_size: Minimum size of the image to be rescaled before feeding it to the backbone.
     Must be a positive integer. Note: training run may get into CUDA OOM if the size is too big.
     Note: This settings is not supported for the 'yolov5' algorithm.
    :paramtype min_size: int
    :keyword model_size: Model size. Must be 'small', 'medium', 'large'.
     Note: training run may get into CUDA OOM if the model size is too big.
     Note: This settings is only supported for the 'yolov5' algorithm. Possible values include:
     "None", "Small", "Medium", "Large", "ExtraLarge".
    :paramtype model_size: str or ~azure.mgmt.machinelearningservices.models.ModelSize
    :keyword multi_scale: Enable multi-scale image by varying image size by +/- 50%.
     Note: training run may get into CUDA OOM if no sufficient GPU memory.
     Note: This settings is only supported for the 'yolov5' algorithm.
    :paramtype multi_scale: bool
    :keyword nms_iou_threshold: IOU threshold used during inference in NMS post processing. Must be a
     float in the range [0, 1].
    :paramtype nms_iou_threshold: float
    :keyword tile_grid_size: The grid size to use for tiling each image. Note: TileGridSize must not
     be
     None to enable small object detection logic. A string containing two integers in mxn format.
     Note: This settings is not supported for the 'yolov5' algorithm.
    :paramtype tile_grid_size: str
    :keyword tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension. Must be float
     in the range [0, 1).
     Note: This settings is not supported for the 'yolov5' algorithm.
    :paramtype tile_overlap_ratio: float
    :keyword tile_predictions_nms_threshold: The IOU threshold to use to perform NMS while merging
     predictions from tiles and image.
     Used in validation/ inference. Must be float in the range [0, 1].
     Note: This settings is not supported for the 'yolov5' algorithm.
    :paramtype tile_predictions_nms_threshold: float
    :keyword validation_iou_threshold: IOU threshold to use when computing validation metric. Must be
     float in the range [0, 1].
    :paramtype validation_iou_threshold: float
    :keyword validation_metric_type: Metric computation method to use for validation metrics. Possible
     values include: "None", "Coco", "Voc", "CocoVoc".
    :paramtype validation_metric_type: str or
     ~azure.mgmt.machinelearningservices.models.ValidationMetricType
    :keyword log_training_metrics: indicates whether or not to log training metrics
    :paramtype log_training_metrics: str or
     ~azure.mgmt.machinelearningservices.models.LogTrainingMetrics
    :keyword log_validation_loss: indicates whether or not to log validation loss
    :paramtype log_validation_loss: str or
     ~azure.mgmt.machinelearningservices.models.LogValidationLoss

    .. literalinclude:: ../samples/ml_samples_automl_image.py
            :start-after: [START automl.automl_image_job.image_object_detection_model_settings]
            :end-before: [END automl.automl_image_job.image_object_detection_model_settings]
            :language: python
            :dedent: 8
            :caption: Defining the automl image object detection or instance segmentation model settings.
    """

    def __init__(
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
        learning_rate_scheduler: Optional[LearningRateScheduler] = None,
        model_name: Optional[str] = None,
        momentum: Optional[float] = None,
        nesterov: Optional[bool] = None,
        number_of_epochs: Optional[int] = None,
        number_of_workers: Optional[int] = None,
        optimizer: Optional[StochasticOptimizer] = None,
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
        model_size: Optional[ModelSize] = None,
        multi_scale: Optional[bool] = None,
        nms_iou_threshold: Optional[float] = None,
        tile_grid_size: Optional[str] = None,
        tile_overlap_ratio: Optional[float] = None,
        tile_predictions_nms_threshold: Optional[float] = None,
        validation_iou_threshold: Optional[float] = None,
        validation_metric_type: Optional[ValidationMetricType] = None,
        log_training_metrics: Optional[LogTrainingMetrics] = None,
        log_validation_loss: Optional[LogValidationLoss] = None,
        **kwargs: Any,
    ):
        super(ImageModelSettingsObjectDetection, self).__init__(
            advanced_settings=advanced_settings,
            ams_gradient=ams_gradient,
            beta1=beta1,
            beta2=beta2,
            checkpoint_frequency=checkpoint_frequency,
            checkpoint_run_id=checkpoint_run_id,
            distributed=distributed,
            early_stopping=early_stopping,
            early_stopping_delay=early_stopping_delay,
            early_stopping_patience=early_stopping_patience,
            enable_onnx_normalization=enable_onnx_normalization,
            evaluation_frequency=evaluation_frequency,
            gradient_accumulation_step=gradient_accumulation_step,
            layers_to_freeze=layers_to_freeze,
            learning_rate=learning_rate,
            learning_rate_scheduler=learning_rate_scheduler,
            model_name=model_name,
            momentum=momentum,
            nesterov=nesterov,
            number_of_epochs=number_of_epochs,
            number_of_workers=number_of_workers,
            optimizer=optimizer,
            random_seed=random_seed,
            step_lr_gamma=step_lr_gamma,
            step_lr_step_size=step_lr_step_size,
            training_batch_size=training_batch_size,
            validation_batch_size=validation_batch_size,
            warmup_cosine_lr_cycles=warmup_cosine_lr_cycles,
            warmup_cosine_lr_warmup_epochs=warmup_cosine_lr_warmup_epochs,
            weight_decay=weight_decay,
            **kwargs,
        )
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
        self.log_training_metrics = log_training_metrics
        self.log_validation_loss = log_validation_loss

    def _to_rest_object(self) -> RestImageModelSettingsObjectDetection:
        return RestImageModelSettingsObjectDetection(
            advanced_settings=self.advanced_settings,
            ams_gradient=self.ams_gradient,
            beta1=self.beta1,
            beta2=self.beta2,
            checkpoint_frequency=self.checkpoint_frequency,
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
            validation_metric_type=self.validation_metric_type,
            log_training_metrics=self.log_training_metrics,
            log_validation_loss=self.log_validation_loss,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestImageModelSettingsObjectDetection) -> "ImageModelSettingsObjectDetection":
        return cls(
            advanced_settings=obj.advanced_settings,
            ams_gradient=obj.ams_gradient,
            beta1=obj.beta1,
            beta2=obj.beta2,
            checkpoint_frequency=obj.checkpoint_frequency,
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
            validation_metric_type=obj.validation_metric_type,
            log_training_metrics=obj.log_training_metrics,
            log_validation_loss=obj.log_validation_loss,
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
            and self.nms_iou_threshold == other.nms_iou_threshold
            and self.tile_grid_size == other.tile_grid_size
            and self.tile_overlap_ratio == other.tile_overlap_ratio
            and self.tile_predictions_nms_threshold == other.tile_predictions_nms_threshold
            and self.validation_iou_threshold == other.validation_iou_threshold
            and self.validation_metric_type == other.validation_metric_type
            and self.log_training_metrics == other.log_training_metrics
            and self.log_validation_loss == other.log_validation_loss
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
