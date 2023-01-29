# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import json

from marshmallow import INCLUDE, fields, pre_dump

from azure.ai.ml._schema.core.fields import DataBindingStr, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml.constants._component import ControlFlowType

from ..job.input_output_entry import OutputSchema
from ..job.job_limits import DoWhileLimitsSchema
from .component_job import _resolve_outputs
from .pipeline_job_io import OutputBindingStr

# pylint: disable=no-self-use,protected-access


class ControlFlowSchema(PathAwareSchema):
    unknown = INCLUDE


class BaseLoopSchema(ControlFlowSchema):
    unknown = INCLUDE
    body = DataBindingStr()

    @pre_dump
    def convert_control_flow_body_to_binding_str(self, data, **kwargs):  # pylint: disable=no-self-use, unused-argument

        result = copy.copy(data)
        # Update body object to data_binding_str
        result._body = data._get_body_binding_str()
        return result


class DoWhileSchema(BaseLoopSchema):
    # pylint: disable=unused-argument
    type = StringTransformedEnum(allowed_values=[ControlFlowType.DO_WHILE])
    condition = UnionField(
        [
            DataBindingStr(),
            fields.Str(),
        ]
    )
    mapping = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                fields.List(fields.Str()),
                fields.Str(),
            ]
        ),
        required=True,
    )
    limits = NestedField(DoWhileLimitsSchema)

    @pre_dump
    def resolve_inputs_outputs(self, data, **kwargs):  # pylint: disable=no-self-use
        # Try resolve object's mapping and condition and return a resolved new object
        result = copy.copy(data)
        mapping = {}
        for k, v in result.mapping.items():
            v = v if isinstance(v, list) else [v]
            mapping[k] = [item._port_name for item in v]
        result._mapping = mapping

        try:
            result._condition = result._condition._port_name
        except AttributeError:
            result._condition = result._condition

        return result


class ParallelForSchema(BaseLoopSchema):
    type = StringTransformedEnum(allowed_values=[ControlFlowType.PARALLEL_FOR])
    items = UnionField(
        [
            fields.Str(),
            fields.Dict(keys=fields.Str(), values=fields.Dict()),
            fields.List(fields.Dict()),
        ],
        required=True,
    )
    max_concurrency = fields.Int()
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([OutputBindingStr, NestedField(OutputSchema)], allow_none=True),
    )

    @pre_dump
    def serialize_items(self, data, **kwargs):  # pylint: disable=no-self-use, unused-argument
        from azure.ai.ml.entities._job.pipeline._io import InputOutputBase

        result = copy.copy(data)
        if isinstance(result.items, (dict, list)):
            # use str to serialize input/output builder
            result._items = json.dumps(result.items, default=lambda x: str(x) if isinstance(x, InputOutputBase) else x)
        return result

    @pre_dump
    def resolve_outputs(self, job, **kwargs):  # pylint: disable=unused-argument

        result = copy.copy(job)
        _resolve_outputs(result, job)
        return result
