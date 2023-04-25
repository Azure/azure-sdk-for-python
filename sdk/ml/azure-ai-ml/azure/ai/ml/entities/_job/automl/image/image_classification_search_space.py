# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=R0902,too-many-locals

from typing import Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import ImageModelDistributionSettingsClassification
from azure.ai.ml.entities._job.automl.search_space import SearchSpace
from azure.ai.ml.entities._job.automl.search_space_utils import _convert_from_rest_object, _convert_to_rest_object
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ImageClassificationSearchSpace(RestTranslatableMixin):
    """Search space for AutoML Image Classification and Image Classification
    Multilabel tasks.

    :param ams_gradient: Enable AMSGrad when optimizer is 'adam' or 'adamw'.
    :type ams_gradient: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
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
        see: https://docs.microsoft.com/en-us/azure/machine-learning/reference-automl-images-hyperparameters#model-agnostic-hyperparameters.    # pylint: disable=line-too-long
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
    :type validation_batch_size: str or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param warmup_cosine_lr_cycles: Value of cosine cycle when learning rate scheduler is
        'warmup_cosine'. Must be a float in the range [0, 1].
    :type warmup_cosine_lr_cycles: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param warmup_cosine_lr_warmup_epochs: Value of warmup epochs when learning rate scheduler is
        'warmup_cosine'. Must be a positive integer.
    :type warmup_cosine_lr_warmup_epochs: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param weight_decay: Value of weight decay when optimizer is 'sgd', 'adam', or 'adamw'. Must
        be a float in the range[0, 1].
    :type weight_decay: float or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param training_crop_size: Image crop size that is input to the neural network for the
        training dataset. Must be a positive integer.
    :type training_crop_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param validation_crop_size: Image crop size that is input to the neural network for the
        validation dataset. Must be a positive integer.
    :type validation_crop_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param validation_resize_size: Image size to which to resize before cropping for validation
        dataset. Must be a positive integer.
    :type validation_resize_size: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    :param weighted_loss: Weighted loss. The accepted values are 0 for no weighted loss.
        1 for weighted loss with sqrt.(class_weights). 2 for weighted loss with class_weights. Must be
        0 or 1 or 2.
    :type weighted_loss: int or ~azure.ai.ml.entities._job.sweep.search_space.SweepDistribution
    """

    def __init__(
        self,
        *,
        ams_gradient: Optional[Union[bool, SweepDistribution]] = None,
        beta1: Optional[Union[float, SweepDistribution]] = None,
        beta2: Optional[Union[float, SweepDistribution]] = None,
        distributed: Optional[Union[bool, SweepDistribution]] = None,
        early_stopping: Optional[Union[bool, SweepDistribution]] = None,
        early_stopping_delay: Optional[Union[int, SweepDistribution]] = None,
        early_stopping_patience: Optional[Union[int, SweepDistribution]] = None,
        enable_onnx_normalization: Optional[Union[bool, SweepDistribution]] = None,
        evaluation_frequency: Optional[Union[int, SweepDistribution]] = None,
        gradient_accumulation_step: Optional[Union[int, SweepDistribution]] = None,
        layers_to_freeze: Optional[Union[int, SweepDistribution]] = None,
        learning_rate: Optional[Union[float, SweepDistribution]] = None,
        learning_rate_scheduler: Optional[Union[str, SweepDistribution]] = None,
        model_name: Optional[Union[str, SweepDistribution]] = None,
        momentum: Optional[Union[float, SweepDistribution]] = None,
        nesterov: Optional[Union[bool, SweepDistribution]] = None,
        number_of_epochs: Optional[Union[int, SweepDistribution]] = None,
        number_of_workers: Optional[Union[int, SweepDistribution]] = None,
        optimizer: Optional[Union[str, SweepDistribution]] = None,
        random_seed: Optional[Union[int, SweepDistribution]] = None,
        step_lr_gamma: Optional[Union[float, SweepDistribution]] = None,
        step_lr_step_size: Optional[Union[int, SweepDistribution]] = None,
        training_batch_size: Optional[Union[int, SweepDistribution]] = None,
        validation_batch_size: Optional[Union[int, SweepDistribution]] = None,
        warmup_cosine_lr_cycles: Optional[Union[float, SweepDistribution]] = None,
        warmup_cosine_lr_warmup_epochs: Optional[Union[int, SweepDistribution]] = None,
        weight_decay: Optional[Union[float, SweepDistribution]] = None,
        training_crop_size: Optional[Union[int, SweepDistribution]] = None,
        validation_crop_size: Optional[Union[int, SweepDistribution]] = None,
        validation_resize_size: Optional[Union[int, SweepDistribution]] = None,
        weighted_loss: Optional[Union[int, SweepDistribution]] = None,
    ) -> None:
        self.ams_gradient = ams_gradient
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
        self.training_crop_size = training_crop_size
        self.validation_crop_size = validation_crop_size
        self.validation_resize_size = validation_resize_size
        self.weighted_loss = weighted_loss

    def _to_rest_object(self) -> ImageModelDistributionSettingsClassification:
        return ImageModelDistributionSettingsClassification(
            ams_gradient=_convert_to_rest_object(self.ams_gradient) if self.ams_gradient is not None else None,
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
            training_crop_size=(
                _convert_to_rest_object(self.training_crop_size) if self.training_crop_size is not None else None
            ),
            validation_crop_size=(
                _convert_to_rest_object(self.validation_crop_size) if self.validation_crop_size is not None else None
            ),
            validation_resize_size=(
                _convert_to_rest_object(self.validation_resize_size)
                if self.validation_resize_size is not None
                else None
            ),
            weighted_loss=_convert_to_rest_object(self.weighted_loss) if self.weighted_loss is not None else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: ImageModelDistributionSettingsClassification) -> "ImageClassificationSearchSpace":
        return cls(
            ams_gradient=_convert_from_rest_object(obj.ams_gradient) if obj.ams_gradient is not None else None,
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
            training_crop_size=(
                _convert_from_rest_object(obj.training_crop_size) if obj.training_crop_size is not None else None
            ),
            validation_crop_size=(
                _convert_from_rest_object(obj.validation_crop_size) if obj.validation_crop_size is not None else None
            ),
            validation_resize_size=(
                _convert_from_rest_object(obj.validation_resize_size)
                if obj.validation_resize_size is not None
                else None
            ),
            weighted_loss=_convert_from_rest_object(obj.weighted_loss) if obj.weighted_loss is not None else None,
        )

    @classmethod
    def _from_search_space_object(cls, obj: SearchSpace) -> "ImageClassificationSearchSpace":
        return cls(
            ams_gradient=obj.ams_gradient if hasattr(obj, "ams_gradient") else None,
            beta1=obj.beta1 if hasattr(obj, "beta1") else None,
            beta2=obj.beta2 if hasattr(obj, "beta2") else None,
            distributed=obj.distributed if hasattr(obj, "distributed") else None,
            early_stopping=obj.early_stopping if hasattr(obj, "early_stopping") else None,
            early_stopping_delay=obj.early_stopping_delay if hasattr(obj, "early_stopping_delay") else None,
            early_stopping_patience=obj.early_stopping_patience if hasattr(obj, "early_stopping_patience") else None,
            enable_onnx_normalization=obj.enable_onnx_normalization
            if hasattr(obj, "enable_onnx_normalization")
            else None,
            evaluation_frequency=obj.evaluation_frequency if hasattr(obj, "evaluation_frequency") else None,
            gradient_accumulation_step=obj.gradient_accumulation_step
            if hasattr(obj, "gradient_accumulation_step")
            else None,
            layers_to_freeze=obj.layers_to_freeze if hasattr(obj, "layers_to_freeze") else None,
            learning_rate=obj.learning_rate if hasattr(obj, "learning_rate") else None,
            learning_rate_scheduler=obj.learning_rate_scheduler if hasattr(obj, "learning_rate_scheduler") else None,
            model_name=obj.model_name if hasattr(obj, "model_name") else None,
            momentum=obj.momentum if hasattr(obj, "momentum") else None,
            nesterov=obj.nesterov if hasattr(obj, "nesterov") else None,
            number_of_epochs=obj.number_of_epochs if hasattr(obj, "number_of_epochs") else None,
            number_of_workers=obj.number_of_workers if hasattr(obj, "number_of_workers") else None,
            optimizer=obj.optimizer if hasattr(obj, "optimizer") else None,
            random_seed=obj.random_seed if hasattr(obj, "random_seed") else None,
            step_lr_gamma=obj.step_lr_gamma if hasattr(obj, "step_lr_gamma") else None,
            step_lr_step_size=obj.step_lr_step_size if hasattr(obj, "step_lr_step_size") else None,
            training_batch_size=obj.training_batch_size if hasattr(obj, "training_batch_size") else None,
            validation_batch_size=obj.validation_batch_size if hasattr(obj, "validation_batch_size") else None,
            warmup_cosine_lr_cycles=obj.warmup_cosine_lr_cycles if hasattr(obj, "warmup_cosine_lr_cycles") else None,
            warmup_cosine_lr_warmup_epochs=obj.warmup_cosine_lr_warmup_epochs
            if hasattr(obj, "warmup_cosine_lr_warmup_epochs")
            else None,
            weight_decay=obj.weight_decay if hasattr(obj, "weight_decay") else None,
            training_crop_size=obj.training_crop_size if hasattr(obj, "training_crop_size") else None,
            validation_crop_size=obj.validation_crop_size if hasattr(obj, "validation_crop_size") else None,
            validation_resize_size=obj.validation_resize_size if hasattr(obj, "validation_resize_size") else None,
            weighted_loss=obj.weighted_loss if hasattr(obj, "weighted_loss") else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageClassificationSearchSpace):
            return NotImplemented

        return (
            self.ams_gradient == other.ams_gradient
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
            and self.training_crop_size == other.training_crop_size
            and self.validation_crop_size == other.validation_crop_size
            and self.validation_resize_size == other.validation_resize_size
            and self.weighted_loss == other.weighted_loss
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
