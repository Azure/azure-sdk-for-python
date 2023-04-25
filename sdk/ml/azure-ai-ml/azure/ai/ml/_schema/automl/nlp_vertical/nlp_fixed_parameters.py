# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import NlpLearningRateScheduler
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_kebab
from azure.ai.ml.constants import NlpModels


class NlpFixedParametersSchema(metaclass=PatchedSchemaMeta):
    gradient_accumulation_steps = fields.Int()
    learning_rate = fields.Float()
    learning_rate_scheduler = StringTransformedEnum(
        allowed_values=[obj.value for obj in NlpLearningRateScheduler],
        casing_transform=camel_to_snake,
    )
    model_name = StringTransformedEnum(
        allowed_values=[obj.value for obj in NlpModels],
        casing_transform=snake_to_kebab,
    )
    number_of_epochs = fields.Int()
    training_batch_size = fields.Int()
    validation_batch_size = fields.Int()
    warmup_ratio = fields.Float()
    weight_decay = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import NlpFixedParameters

        return NlpFixedParameters(**data)
