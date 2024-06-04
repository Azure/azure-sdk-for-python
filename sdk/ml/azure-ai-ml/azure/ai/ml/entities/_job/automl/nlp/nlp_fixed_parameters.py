# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import NlpFixedParameters as RestNlpFixedParameters
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class NlpFixedParameters(RestTranslatableMixin):
    """Configuration of fixed parameters for all candidates of an AutoML NLP Job

    :param gradient_accumulation_steps: number of steps over which to accumulate gradients before a backward
            pass. This must be a positive integer, defaults to None
    :type gradient_accumulation_steps: Optional[int]
    :param learning_rate: initial learning rate. Must be a float in (0, 1), defaults to None
    :type learning_rate: Optional[float]
    :param learning_rate_scheduler: the type of learning rate scheduler. Must choose from 'linear', 'cosine',
            'cosine_with_restarts', 'polynomial', 'constant', and 'constant_with_warmup', defaults to None
    :type learning_rate_scheduler: Optional[str]
    :param model_name: the model name to use during training. Must choose from 'bert-base-cased',
            'bert-base-uncased', 'bert-base-multilingual-cased', 'bert-base-german-cased', 'bert-large-cased',
            'bert-large-uncased', 'distilbert-base-cased', 'distilbert-base-uncased', 'roberta-base', 'roberta-large',
            'distilroberta-base', 'xlm-roberta-base', 'xlm-roberta-large', xlnet-base-cased', and 'xlnet-large-cased',
            defaults to None
    :type model_name: Optional[str]
    :param number_of_epochs: the number of epochs to train with. Must be a positive integer, defaults to None
    :type number_of_epochs: Optional[int]
    :param training_batch_size: the batch size during training. Must be a positive integer, defaults to None
    :type training_batch_size: Optional[int]
    :param validation_batch_size: the batch size during validation. Must be a positive integer, defaults to None
    :type validation_batch_size: Optional[int]
    :param warmup_ratio: ratio of total training steps used for a linear warmup from 0 to learning_rate.
            Must be a float in [0, 1], defaults to None
    :type warmup_ratio: Optional[float]
    :param weight_decay: value of weight decay when optimizer is sgd, adam, or adamw. This must be a float in
            the range [0, 1] defaults to None
    :type weight_decay: Optional[float]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.nlp_fixed_parameters]
                :end-before: [END automl.nlp_fixed_parameters]
                :language: python
                :dedent: 8
                :caption: creating an nlp fixed parameters
    """

    def __init__(
        self,
        *,
        gradient_accumulation_steps: Optional[int] = None,
        learning_rate: Optional[float] = None,
        learning_rate_scheduler: Optional[str] = None,
        model_name: Optional[str] = None,
        number_of_epochs: Optional[int] = None,
        training_batch_size: Optional[int] = None,
        validation_batch_size: Optional[int] = None,
        warmup_ratio: Optional[float] = None,
        weight_decay: Optional[float] = None,
    ):
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.learning_rate = learning_rate
        self.learning_rate_scheduler = learning_rate_scheduler
        self.model_name = model_name
        self.number_of_epochs = number_of_epochs
        self.training_batch_size = training_batch_size
        self.validation_batch_size = validation_batch_size
        self.warmup_ratio = warmup_ratio
        self.weight_decay = weight_decay

    def _to_rest_object(self) -> RestNlpFixedParameters:
        return RestNlpFixedParameters(
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            learning_rate=self.learning_rate,
            learning_rate_scheduler=self.learning_rate_scheduler,
            model_name=self.model_name,
            number_of_epochs=self.number_of_epochs,
            training_batch_size=self.training_batch_size,
            validation_batch_size=self.validation_batch_size,
            warmup_ratio=self.warmup_ratio,
            weight_decay=self.weight_decay,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestNlpFixedParameters) -> "NlpFixedParameters":
        return cls(
            gradient_accumulation_steps=obj.gradient_accumulation_steps,
            learning_rate=obj.learning_rate,
            learning_rate_scheduler=obj.learning_rate_scheduler,
            model_name=obj.model_name,
            number_of_epochs=obj.number_of_epochs,
            training_batch_size=obj.training_batch_size,
            validation_batch_size=obj.validation_batch_size,
            warmup_ratio=obj.warmup_ratio,
            weight_decay=obj.weight_decay,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NlpFixedParameters):
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
