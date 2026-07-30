# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional, Union

from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import NlpModels
from azure.ai.ml.constants._job.automl import NlpLearningRateScheduler
from azure.ai.ml.entities._job.automl.search_space import SearchSpace
from azure.ai.ml.entities._job.automl.search_space_utils import _convert_from_rest_object, _convert_to_rest_object
from azure.ai.ml.entities._job.sweep.search_space import Choice, SweepDistribution
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class NlpSearchSpace(RestTranslatableMixin):
    """Search space for AutoML NLP tasks.

    :param gradient_accumulation_steps: number of steps over which to accumulate gradients before a backward
        pass. This must be a positive integer., defaults to None
    :type gradient_accumulation_steps: Optional[Union[int, SweepDistribution]]
    :param learning_rate: initial learning rate. Must be a float in (0, 1), defaults to None
    :type learning_rate: Optional[Union[float, SweepDistribution]]
    :param learning_rate_scheduler: the type of learning rate scheduler. Must choose from 'linear', 'cosine',
        'cosine_with_restarts', 'polynomial', 'constant', and 'constant_with_warmup', defaults to None
    :type learning_rate_scheduler: Optional[Union[str, SweepDistribution]]
    :param model_name: the model name to use during training. Must choose from 'bert-base-cased',
        'bert-base-uncased', 'bert-base-multilingual-cased', 'bert-base-german-cased', 'bert-large-cased',
        'bert-large-uncased', 'distilbert-base-cased', 'distilbert-base-uncased', 'roberta-base', 'roberta-large',
        'distilroberta-base', 'xlm-roberta-base', 'xlm-roberta-large', xlnet-base-cased', and 'xlnet-large-cased',
        defaults to None
    :type model_name: Optional[Union[str, SweepDistribution]]
    :param number_of_epochs: the number of epochs to train with. Must be a positive integer, defaults to None
    :type number_of_epochs: Optional[Union[int, SweepDistribution]]
    :param training_batch_size: the batch size during training. Must be a positive integer, defaults to None
    :type training_batch_size: Optional[Union[int, SweepDistribution]]
    :param validation_batch_size: the batch size during validation. Must be a positive integer, defaults to None
    :type validation_batch_size: Optional[Union[int, SweepDistribution]]
    :param warmup_ratio: ratio of total training steps used for a linear warmup from 0 to learning_rate.
            Must be a float in [0, 1], defaults to None
    :type warmup_ratio: Optional[Union[float, SweepDistribution]]
    :param weight_decay: value of weight decay when optimizer is sgd, adam, or adamw. This must be a float in
            the range [0, 1], defaults to None
    :type weight_decay: Optional[Union[float, SweepDistribution]]


    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.nlp_search_space]
                :end-before: [END automl.nlp_search_space]
                :language: python
                :dedent: 8
                :caption: creating an nlp search space
    """

    def __init__(
        self,
        *,
        gradient_accumulation_steps: Optional[Union[int, SweepDistribution]] = None,
        learning_rate: Optional[Union[float, SweepDistribution]] = None,
        learning_rate_scheduler: Optional[Union[str, SweepDistribution]] = None,
        model_name: Optional[Union[str, SweepDistribution]] = None,
        number_of_epochs: Optional[Union[int, SweepDistribution]] = None,
        training_batch_size: Optional[Union[int, SweepDistribution]] = None,
        validation_batch_size: Optional[Union[int, SweepDistribution]] = None,
        warmup_ratio: Optional[Union[float, SweepDistribution]] = None,
        weight_decay: Optional[Union[float, SweepDistribution]] = None
    ):
        # Since we want customers to be able to specify enums as well rather than just strings, we need to access
        # the enum values here before we serialize them ('NlpModels.BERT_BASE_CASED' vs. 'bert-base-cased').
        if isinstance(learning_rate_scheduler, NlpLearningRateScheduler):
            learning_rate_scheduler = camel_to_snake(learning_rate_scheduler.value)
        elif isinstance(learning_rate_scheduler, Choice):
            if learning_rate_scheduler.values is not None:
                learning_rate_scheduler.values = [
                    camel_to_snake(item.value) if isinstance(item, NlpLearningRateScheduler) else item
                    for item in learning_rate_scheduler.values
                ]

        if isinstance(model_name, NlpModels):
            model_name = model_name.value
        elif isinstance(model_name, Choice):
            if model_name.values is not None:
                model_name.values = [item.value if isinstance(item, NlpModels) else item for item in model_name.values]

        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.learning_rate = learning_rate
        self.learning_rate_scheduler = learning_rate_scheduler
        self.model_name = model_name
        self.number_of_epochs = number_of_epochs
        self.training_batch_size = training_batch_size
        self.validation_batch_size = validation_batch_size
        self.warmup_ratio = warmup_ratio
        self.weight_decay = weight_decay

    def _to_rest_object(self) -> Dict[str, Any]:
        # ``NlpParameterSubspace`` was dropped from the arm_ml_service (2025-12) model set; emit the
        # camelCase wire dict directly so it round-trips through ``SdkJSONEncoder``.
        return {
            "gradientAccumulationSteps": (
                _convert_to_rest_object(self.gradient_accumulation_steps)
                if self.gradient_accumulation_steps is not None
                else None
            ),
            "learningRate": _convert_to_rest_object(self.learning_rate) if self.learning_rate is not None else None,
            "learningRateScheduler": (
                _convert_to_rest_object(self.learning_rate_scheduler)
                if self.learning_rate_scheduler is not None
                else None
            ),
            "modelName": _convert_to_rest_object(self.model_name) if self.model_name is not None else None,
            "numberOfEpochs": (
                _convert_to_rest_object(self.number_of_epochs) if self.number_of_epochs is not None else None
            ),
            "trainingBatchSize": (
                _convert_to_rest_object(self.training_batch_size) if self.training_batch_size is not None else None
            ),
            "validationBatchSize": (
                _convert_to_rest_object(self.validation_batch_size) if self.validation_batch_size is not None else None
            ),
            "warmupRatio": _convert_to_rest_object(self.warmup_ratio) if self.warmup_ratio is not None else None,
            "weightDecay": _convert_to_rest_object(self.weight_decay) if self.weight_decay is not None else None,
        }

    @classmethod
    def _from_rest_object(cls, obj: Dict[str, Any]) -> "NlpSearchSpace":
        return cls(
            gradient_accumulation_steps=(
                _convert_from_rest_object(obj.get("gradientAccumulationSteps"))
                if obj.get("gradientAccumulationSteps") is not None
                else None
            ),
            learning_rate=(
                _convert_from_rest_object(obj.get("learningRate")) if obj.get("learningRate") is not None else None
            ),
            learning_rate_scheduler=(
                _convert_from_rest_object(obj.get("learningRateScheduler"))
                if obj.get("learningRateScheduler") is not None
                else None
            ),
            model_name=_convert_from_rest_object(obj.get("modelName")) if obj.get("modelName") is not None else None,
            number_of_epochs=(
                _convert_from_rest_object(obj.get("numberOfEpochs")) if obj.get("numberOfEpochs") is not None else None
            ),
            training_batch_size=(
                _convert_from_rest_object(obj.get("trainingBatchSize"))
                if obj.get("trainingBatchSize") is not None
                else None
            ),
            validation_batch_size=(
                _convert_from_rest_object(obj.get("validationBatchSize"))
                if obj.get("validationBatchSize") is not None
                else None
            ),
            warmup_ratio=(
                _convert_from_rest_object(obj.get("warmupRatio")) if obj.get("warmupRatio") is not None else None
            ),
            weight_decay=(
                _convert_from_rest_object(obj.get("weightDecay")) if obj.get("weightDecay") is not None else None
            ),
        )

    @classmethod
    def _from_search_space_object(cls, obj: SearchSpace) -> "NlpSearchSpace":
        return cls(
            gradient_accumulation_steps=(
                obj.gradient_accumulation_steps if hasattr(obj, "gradient_accumulation_steps") else None
            ),
            learning_rate=obj.learning_rate if hasattr(obj, "learning_rate") else None,
            learning_rate_scheduler=obj.learning_rate_scheduler if hasattr(obj, "learning_rate_scheduler") else None,
            model_name=obj.model_name if hasattr(obj, "model_name") else None,
            number_of_epochs=obj.number_of_epochs if hasattr(obj, "number_of_epochs") else None,
            training_batch_size=obj.training_batch_size if hasattr(obj, "training_batch_size") else None,
            validation_batch_size=obj.validation_batch_size if hasattr(obj, "validation_batch_size") else None,
            warmup_ratio=obj.warmup_ratio if hasattr(obj, "warmup_ratio") else None,
            weight_decay=obj.weight_decay if hasattr(obj, "weight_decay") else None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NlpSearchSpace):
            return NotImplemented

        return (
            self.gradient_accumulation_steps == other.gradient_accumulation_steps
            and self.learning_rate == other.learning_rate
            and self.learning_rate_scheduler == other.learning_rate_scheduler
            and self.model_name == other.model_name
            and self.number_of_epochs == other.number_of_epochs
            and self.training_batch_size == other.training_batch_size
            and self.validation_batch_size == other.validation_batch_size
            and self.warmup_ratio == other.warmup_ratio
            and self.weight_decay == other.weight_decay
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
