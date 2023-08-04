# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,protected-access

from marshmallow import fields, post_dump, post_load, pre_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import NlpLearningRateScheduler
from azure.ai.ml._schema._sweep.search_space import (
    ChoiceSchema,
    NormalSchema,
    QNormalSchema,
    QUniformSchema,
    RandintSchema,
    UniformSchema,
)
from azure.ai.ml._schema.core.fields import (
    DumpableIntegerField,
    DumpableStringField,
    NestedField,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake


def choice_schema_of_type(cls, **kwargs):
    class CustomChoiceSchema(ChoiceSchema):
        values = fields.List(cls(**kwargs))

    return CustomChoiceSchema()


def choice_and_single_value_schema_of_type(cls, **kwargs):
    return UnionField([cls(**kwargs), NestedField(choice_schema_of_type(cls, **kwargs))])


FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD = UnionField(
    [
        fields.Float(),
        DumpableIntegerField(strict=True),
        NestedField(choice_schema_of_type(DumpableIntegerField, strict=True)),
        NestedField(choice_schema_of_type(fields.Float)),
        NestedField(UniformSchema()),
        NestedField(QUniformSchema()),
        NestedField(NormalSchema()),
        NestedField(QNormalSchema()),
        NestedField(RandintSchema()),
    ]
)

INT_SEARCH_SPACE_DISTRIBUTION_FIELD = UnionField(
    [
        DumpableIntegerField(strict=True),
        NestedField(choice_schema_of_type(DumpableIntegerField, strict=True)),
        NestedField(RandintSchema()),
    ]
)

STRING_SEARCH_SPACE_DISTRIBUTION_FIELD = choice_and_single_value_schema_of_type(DumpableStringField)
BOOL_SEARCH_SPACE_DISTRIBUTION_FIELD = choice_and_single_value_schema_of_type(fields.Bool)


class NlpParameterSubspaceSchema(metaclass=PatchedSchemaMeta):
    gradient_accumulation_steps = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    learning_rate = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    learning_rate_scheduler = choice_and_single_value_schema_of_type(
        StringTransformedEnum,
        allowed_values=[obj.value for obj in NlpLearningRateScheduler],
        casing_transform=camel_to_snake,
    )
    model_name = STRING_SEARCH_SPACE_DISTRIBUTION_FIELD
    number_of_epochs = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    training_batch_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    validation_batch_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    warmup_ratio = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    weight_decay = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD

    @post_dump
    def conversion(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):  # pylint: disable=no-member
            # AutoML job inside pipeline does load(dump) instead of calling to_rest_object
            # explicitly for creating the autoRest Object from sdk job.
            # Hence for pipeline job, we explicitly convert Sweep Distribution dict to str after dump in this method.
            # For standalone automl job, same conversion happens in text_classification_job._to_rest_object()
            from azure.ai.ml.entities._job.automl.search_space_utils import _convert_sweep_dist_dict_to_str_dict

            data = _convert_sweep_dist_dict_to_str_dict(data)
        return data

    @pre_load
    def before_make(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):  # pylint: disable=no-member
            from azure.ai.ml.entities._job.automl.search_space_utils import _convert_sweep_dist_str_to_dict

            # Converting Sweep Distribution str to Sweep Distribution dict for complying with search_space schema.
            data = _convert_sweep_dist_str_to_dict(data)
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import NlpSearchSpace

        return NlpSearchSpace(**data)
