# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml.constants._monitoring import MonitorDatasetContext
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.job.input_output_entry import MLTableInputSchema, DataInputSchema


class MonitorInputDataSchema(metaclass=PatchedSchemaMeta):
    input_data = UnionField(union_fields=[NestedField(DataInputSchema), NestedField(MLTableInputSchema)])
    data_context = StringTransformedEnum(allowed_values=[o.value for o in MonitorDatasetContext])
    target_column_name = fields.Str()
    job_type = fields.Str()
    uri = fields.Str()


class FixedInputDataSchema(MonitorInputDataSchema):
    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.input_data import FixedInputData
        return FixedInputData(**data)
    
class TrailingInputDataSchema(MonitorInputDataSchema):
    trailing_window_size = fields.Str()
    trailing_window_offset = fields.Str()
    pre_processing_component = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.input_data import TrailingInputData
        return TrailingInputData(**data)
    
class StaticInputDataSchema(MonitorInputDataSchema):
    pre_processing_component = fields.Str()
    window_start = fields.DateTime()
    window_end = fields.DateTime()


    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.input_data import StaticInputData
        return StaticInputData(**data)
