# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    LogVerbosity,
    NlpLearningRateScheduler,
    SamplingAlgorithmType,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_vertical import AutoMLVertical
from azure.ai.ml.entities._job.automl.nlp.nlp_featurization_settings import NlpFeaturizationSettings
from azure.ai.ml.entities._job.automl.nlp.nlp_fixed_parameters import NlpFixedParameters
from azure.ai.ml.entities._job.automl.nlp.nlp_limit_settings import NlpLimitSettings
from azure.ai.ml.entities._job.automl.nlp.nlp_search_space import NlpSearchSpace
from azure.ai.ml.entities._job.automl.nlp.nlp_sweep_settings import NlpSweepSettings
from azure.ai.ml.entities._job.automl.search_space import SearchSpace
from azure.ai.ml.entities._job.automl.utils import cast_to_specific_search_space
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


# pylint: disable=too-many-instance-attributes,protected-access
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
        featurization: Optional[NlpFeaturizationSettings] = None,
        limits: Optional[NlpLimitSettings] = None,
        sweep: Optional[NlpSweepSettings] = None,
        training_parameters: Optional[NlpFixedParameters] = None,
        search_space: Optional[List[NlpSearchSpace]] = None,
        **kwargs,
    ):
        super().__init__(task_type, training_data=training_data, validation_data=validation_data, **kwargs)
        self.log_verbosity = log_verbosity
        self.primary_metric = primary_metric

        self.target_column_name = target_column_name

        self._featurization = featurization
        self._limits = limits or NlpLimitSettings()
        self._sweep = sweep
        self.training_parameters = training_parameters  # via setter method.
        self._search_space = search_space

    @property
    def training_parameters(self) -> NlpFixedParameters:
        return self._training_parameters

    @training_parameters.setter
    def training_parameters(self, value: Union[Dict, NlpFixedParameters]) -> None:
        if value is None:
            self._training_parameters = None
        elif isinstance(value, NlpFixedParameters):
            self._training_parameters = value
            # Convert parameters from snake case to enum.
            self.set_training_parameters(learning_rate_scheduler=value.learning_rate_scheduler)
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for nlp training parameters."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_training_parameters(**value)

    @property
    def search_space(self) -> List[NlpSearchSpace]:
        return self._search_space

    @search_space.setter
    def search_space(self, value: Union[List[dict], List[SearchSpace]]) -> None:
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

        if not (all_search_space_type or all_dict_type):
            msg = "Expected all items in the list to be either dictionaries or SearchSpace objects."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )

        self._search_space = [cast_to_specific_search_space(item, NlpSearchSpace, self.task_type) for item in value]

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
    def sweep(self) -> NlpSweepSettings:
        return self._sweep

    @sweep.setter
    def sweep(self, value: Union[Dict, NlpSweepSettings]) -> None:
        if isinstance(value, NlpSweepSettings):
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

    def set_limits(
        self,
        *,
        max_trials: int = 1,
        max_concurrent_trials: int = 1,
        max_nodes: int = 1,
        timeout_minutes: Optional[int] = None,
        trial_timeout_minutes: Optional[int] = None,
    ) -> None:
        self._limits = NlpLimitSettings(
            max_trials=max_trials,
            max_concurrent_trials=max_concurrent_trials,
            max_nodes=max_nodes,
            timeout_minutes=timeout_minutes,
            trial_timeout_minutes=trial_timeout_minutes,
        )

    def set_sweep(
        self,
        *,
        sampling_algorithm: Union[str, SamplingAlgorithmType],
        early_termination: Optional[EarlyTerminationPolicy] = None,
    ):
        """Sweep settings for all AutoML NLP tasks.

        :param sampling_algorithm: Required. Specifies type of hyperparameter sampling algorithm.
        Possible values include: "Grid", "Random", and "Bayesian".
        :param early_termination: Optional early termination policy to end poorly performing training candidates.
        :return: None.
        """
        if self._sweep:
            self._sweep.sampling_algorithm = sampling_algorithm
        else:
            self._sweep = NlpSweepSettings(sampling_algorithm=sampling_algorithm)

        self._sweep.early_termination = early_termination or self._sweep.early_termination

    def set_training_parameters(
        self,
        *,
        gradient_accumulation_steps: Optional[int] = None,
        learning_rate: Optional[float] = None,
        learning_rate_scheduler: Optional[Union[str, NlpLearningRateScheduler]] = None,
        model_name: Optional[str] = None,
        number_of_epochs: Optional[int] = None,
        training_batch_size: Optional[int] = None,
        validation_batch_size: Optional[int] = None,
        warmup_ratio: Optional[float] = None,
        weight_decay: Optional[float] = None,
    ) -> None:
        """Fix certain training parameters throughout the training procedure for all candidates.

        :param gradient_accumulation_steps: number of steps over which to accumulate gradients before a backward
        pass. This must be a positive integer.
        :param learning_rate: initial learning rate. Must be a float in (0, 1).
        :param learning_rate_scheduler: the type of learning rate scheduler. Must choose from 'linear', 'cosine',
        'cosine_with_restarts', 'polynomial', 'constant', and 'constant_with_warmup'.
        :param model_name: the model name to use during training. Must choose from 'bert-base-cased',
        'bert-base-uncased', 'bert-base-multilingual-cased', 'bert-base-german-cased', 'bert-large-cased',
        'bert-large-uncased', 'distilbert-base-cased', 'distilbert-base-uncased', 'roberta-base', 'roberta-large',
        'distilroberta-base', 'xlm-roberta-base', 'xlm-roberta-large', xlnet-base-cased', and 'xlnet-large-cased'.
        :param number_of_epochs: the number of epochs to train with. Must be a positive integer.
        :param training_batch_size: the batch size during training. Must be a positive integer.
        :param validation_batch_size: the batch size during validation. Must be a positive integer.
        :param warmup_ratio: ratio of total training steps used for a linear warmup from 0 to learning_rate.
        Must be a float in [0, 1].
        :param weight_decay: value of weight decay when optimizer is sgd, adam, or adamw. This must be a float in
        the range [0, 1].
        :return: None.
        """
        self._training_parameters = self._training_parameters or NlpFixedParameters()

        self._training_parameters.gradient_accumulation_steps = (
            gradient_accumulation_steps
            if gradient_accumulation_steps is not None
            else self._training_parameters.gradient_accumulation_steps
        )

        self._training_parameters.learning_rate = (
            learning_rate if learning_rate is not None else self._training_parameters.learning_rate
        )

        self._training_parameters.learning_rate_scheduler = (
            NlpLearningRateScheduler[camel_to_snake(learning_rate_scheduler).upper()]
            if learning_rate_scheduler is not None
            else self._training_parameters.learning_rate_scheduler
        )

        self._training_parameters.model_name = (
            model_name if model_name is not None else self._training_parameters.model_name
        )

        self._training_parameters.number_of_epochs = (
            number_of_epochs if number_of_epochs is not None else self._training_parameters.number_of_epochs
        )

        self._training_parameters.training_batch_size = (
            training_batch_size if training_batch_size is not None else self._training_parameters.training_batch_size
        )

        self._training_parameters.validation_batch_size = (
            validation_batch_size
            if validation_batch_size is not None
            else self._training_parameters.validation_batch_size
        )

        self._training_parameters.warmup_ratio = (
            warmup_ratio if warmup_ratio is not None else self._training_parameters.warmup_ratio
        )

        self._training_parameters.weight_decay = (
            weight_decay if weight_decay is not None else self._training_parameters.weight_decay
        )

    def set_featurization(self, *, dataset_language: Optional[str] = None) -> None:
        self._featurization = NlpFeaturizationSettings(
            dataset_language=dataset_language,
        )

    def extend_search_space(self, value: Union[SearchSpace, List[SearchSpace]]) -> None:
        """Add (a) search space(s) for this AutoML NLP job.

        :param value: either a SearchSpace object or a list of SearchSpace objects with nlp-specific parameters.
        :return: None.
        """
        self._search_space = self._search_space or []
        if isinstance(value, list):
            self._search_space.extend(
                [cast_to_specific_search_space(item, NlpSearchSpace, self.task_type) for item in value]
            )
        else:
            self._search_space.append(cast_to_specific_search_space(value, NlpSearchSpace, self.task_type))

    @classmethod
    def _get_search_space_from_str(cls, search_space_str: Optional[str]) -> Optional[List]:
        if search_space_str is not None:
            return [NlpSearchSpace._from_rest_object(entry) for entry in search_space_str if entry is not None]
        return None

    def _restore_data_inputs(self):
        """Restore MLTableJobInputs to Inputs within data_settings.

        self.training_data and self.validation_data should reflect what user passed in (Input) Once we get response back
        from service (as MLTableJobInput), we should set responsible ones back to Input
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
            and self._sweep == other._sweep
            and self._training_parameters == other._training_parameters
            and self._search_space == other._search_space
        )

    def __ne__(self, other):
        return not self.__eq__(other)
