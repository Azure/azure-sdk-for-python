# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import NlpLearningRateScheduler, NlpParameterSubspace
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import NlpModels
from azure.ai.ml.entities._job.automl.search_space import SearchSpace
from azure.ai.ml.entities._job.automl.search_space_utils import _convert_from_rest_object, _convert_to_rest_object
from azure.ai.ml.entities._job.sweep.search_space import Choice, SweepDistribution
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class NlpSearchSpace(RestTranslatableMixin):
    """Search space for AutoML NLP tasks."""

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
            learning_rate_scheduler.values = [
                camel_to_snake(item.value) if isinstance(item, NlpLearningRateScheduler) else item
                for item in learning_rate_scheduler.values
            ]

        if isinstance(model_name, NlpModels):
            model_name = model_name.value
        elif isinstance(model_name, Choice):
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

    def _to_rest_object(self) -> NlpParameterSubspace:
        return NlpParameterSubspace(
            gradient_accumulation_steps=(
                _convert_to_rest_object(self.gradient_accumulation_steps)
                if self.gradient_accumulation_steps is not None
                else None
            ),
            learning_rate=_convert_to_rest_object(self.learning_rate) if self.learning_rate is not None else None,
            learning_rate_scheduler=(
                _convert_to_rest_object(self.learning_rate_scheduler)
                if self.learning_rate_scheduler is not None
                else None
            ),
            model_name=_convert_to_rest_object(self.model_name) if self.model_name is not None else None,
            number_of_epochs=(
                _convert_to_rest_object(self.number_of_epochs) if self.number_of_epochs is not None else None
            ),
            training_batch_size=(
                _convert_to_rest_object(self.training_batch_size) if self.training_batch_size is not None else None
            ),
            validation_batch_size=(
                _convert_to_rest_object(self.validation_batch_size) if self.validation_batch_size is not None else None
            ),
            warmup_ratio=_convert_to_rest_object(self.warmup_ratio) if self.warmup_ratio is not None else None,
            weight_decay=_convert_to_rest_object(self.weight_decay) if self.weight_decay is not None else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: NlpParameterSubspace) -> "NlpSearchSpace":
        return cls(
            gradient_accumulation_steps=(
                _convert_from_rest_object(obj.gradient_accumulation_steps)
                if obj.gradient_accumulation_steps is not None
                else None
            ),
            learning_rate=_convert_from_rest_object(obj.learning_rate) if obj.learning_rate is not None else None,
            learning_rate_scheduler=(
                _convert_from_rest_object(obj.learning_rate_scheduler)
                if obj.learning_rate_scheduler is not None
                else None
            ),
            model_name=_convert_from_rest_object(obj.model_name) if obj.model_name is not None else None,
            number_of_epochs=(
                _convert_from_rest_object(obj.number_of_epochs) if obj.number_of_epochs is not None else None
            ),
            training_batch_size=(
                _convert_from_rest_object(obj.training_batch_size) if obj.training_batch_size is not None else None
            ),
            validation_batch_size=(
                _convert_from_rest_object(obj.validation_batch_size) if obj.validation_batch_size is not None else None
            ),
            warmup_ratio=_convert_from_rest_object(obj.warmup_ratio) if obj.warmup_ratio is not None else None,
            weight_decay=_convert_from_rest_object(obj.weight_decay) if obj.weight_decay is not None else None,
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
