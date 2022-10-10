# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    LearningRateScheduler,
    StochasticOptimizer,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._job.automl.image.automl_image import AutoMLImage
from azure.ai.ml.entities._job.automl.image.image_classification_search_space import ImageClassificationSearchSpace
from azure.ai.ml.entities._job.automl.image.image_limit_settings import ImageLimitSettings
from azure.ai.ml.entities._job.automl.image.image_model_settings import ImageModelSettingsClassification
from azure.ai.ml.entities._job.automl.image.image_sweep_settings import ImageSweepSettings
from azure.ai.ml.entities._job.automl.search_space import SearchSpace
from azure.ai.ml.entities._job.automl.utils import cast_to_specific_search_space
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class AutoMLImageClassificationBase(AutoMLImage):
    def __init__(
        self,
        *,
        task_type: str,
        limits: ImageLimitSettings = None,
        sweep: ImageSweepSettings = None,
        training_parameters: ImageModelSettingsClassification = None,
        search_space: List[ImageClassificationSearchSpace] = None,
        **kwargs,
    ) -> None:
        super().__init__(task_type=task_type, limits=limits, sweep=sweep, **kwargs)
        self.training_parameters = training_parameters  # Assigning training_parameters through setter method.
        self._search_space = search_space

    @property
    def training_parameters(self) -> ImageModelSettingsClassification:
        return self._training_parameters

    @training_parameters.setter
    def training_parameters(self, value: Union[Dict, ImageModelSettingsClassification]) -> None:
        if value is None:
            self._training_parameters = None
        elif isinstance(value, ImageModelSettingsClassification):
            self._training_parameters = value
            # set_training_parameters convert parameter values from snake case str to enum.
            # We need to add any future enum parameters in this call to support snake case str.
            self.set_training_parameters(
                optimizer=value.optimizer,
                learning_rate_scheduler=value.learning_rate_scheduler,
            )
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
    def search_space(self) -> List[ImageClassificationSearchSpace]:
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
                cast_to_specific_search_space(item, ImageClassificationSearchSpace, self.task_type) for item in value
            ]
        else:
            msg = "Expected all items in the list to be either dictionaries or ImageClassificationSearchSpace objects."
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
        advanced_settings: str = None,
        ams_gradient: bool = None,
        beta1: float = None,
        beta2: float = None,
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
        training_crop_size: int = None,
        validation_crop_size: int = None,
        validation_resize_size: int = None,
        weighted_loss: int = None,
    ) -> None:
        """Setting Image training parameters for AutoML Image Classification and
        Image Classification Multilabel tasks.

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
        :param training_crop_size: Image crop size that is input to the neural network for the
         training dataset. Must be a positive integer.
        :type training_crop_size: int
        :param validation_crop_size: Image crop size that is input to the neural network for the
         validation dataset. Must be a positive integer.
        :type validation_crop_size: int
        :param validation_resize_size: Image size to which to resize before cropping for validation
         dataset. Must be a positive integer.
        :type validation_resize_size: int
        :param weighted_loss: Weighted loss. The accepted values are 0 for no weighted loss.
         1 for weighted loss with sqrt.(class_weights). 2 for weighted loss with class_weights. Must be
         0 or 1 or 2.
        :type weighted_loss: int
        """
        self._training_parameters = self._training_parameters or ImageModelSettingsClassification()

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
            LearningRateScheduler[camel_to_snake(learning_rate_scheduler).upper()]
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
            StochasticOptimizer[camel_to_snake(optimizer).upper()]
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
        self._training_parameters.training_crop_size = (
            training_crop_size if training_crop_size is not None else self._training_parameters.training_crop_size
        )
        self._training_parameters.validation_crop_size = (
            validation_crop_size if validation_crop_size is not None else self._training_parameters.validation_crop_size
        )
        self._training_parameters.validation_resize_size = (
            validation_resize_size
            if validation_resize_size is not None
            else self._training_parameters.validation_resize_size
        )
        self._training_parameters.weighted_loss = (
            weighted_loss if weighted_loss is not None else self._training_parameters.weighted_loss
        )

    # pylint: enable=too-many-locals

    def extend_search_space(
        self,
        value: Union[SearchSpace, List[SearchSpace]],
    ) -> None:
        """Add Search space for AutoML Image Classification and Image
        Classification Multilabel tasks.

        :param value: specify either an instance of ImageClassificationSearchSpace or list of
        ImageClassificationSearchSpace for searching through the parameter space
        :type Union[ImageClassificationSearchSpace, List[ImageClassificationSearchSpace]]
        """
        self._search_space = self._search_space or []

        if isinstance(value, list):
            self._search_space.extend(
                [cast_to_specific_search_space(item, ImageClassificationSearchSpace, self.task_type) for item in value]
            )
        else:
            self._search_space.append(
                cast_to_specific_search_space(value, ImageClassificationSearchSpace, self.task_type)
            )

    @classmethod
    def _get_search_space_from_str(cls, search_space_str: str):
        return (
            [ImageClassificationSearchSpace._from_rest_object(entry) for entry in search_space_str if entry is not None]
            if search_space_str is not None
            else None
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, AutoMLImageClassificationBase):
            return NotImplemented

        if not super().__eq__(other):
            return False

        return self._training_parameters == other._training_parameters and self._search_space == other._search_space

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
