# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import json

from marshmallow import INCLUDE, fields, pre_dump, pre_load

from azure.ai.ml._schema.core.fields import DataBindingStr, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml.constants._component import ControlFlowType

from ..job.input_output_entry import OutputSchema
from ..job.input_output_fields_provider import InputsField
from ..job.job_limits import DoWhileLimitsSchema
from .component_job import _resolve_outputs
from .pipeline_job_io import OutputBindingStr

# pylint: disable=protected-access


class ControlFlowSchema(PathAwareSchema):
    unknown = INCLUDE


class BaseLoopSchema(ControlFlowSchema):
    unknown = INCLUDE
    body = DataBindingStr()

    @pre_dump
    def convert_control_flow_body_to_binding_str(self, data, **kwargs):  # pylint: disable= unused-argument
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
    limits = NestedField(DoWhileLimitsSchema, required=True)

    @pre_dump
    def resolve_inputs_outputs(self, data, **kwargs):
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

    @pre_dump
    def convert_control_flow_body_to_binding_str(self, data, **kwargs):  # pylint: disable= unused-argument
        return super(DoWhileSchema, self).convert_control_flow_body_to_binding_str(data, **kwargs)


class ParallelForSchema(BaseLoopSchema):
    type = StringTransformedEnum(allowed_values=[ControlFlowType.PARALLEL_FOR])
    items = UnionField(
        [
            fields.Dict(keys=fields.Str(), values=InputsField()),
            fields.List(InputsField()),
            # put str in last to make sure other type items won't become string when dumps.
            # TODO: only support binding here
            fields.Str(),
        ],
        required=True,
    )
    max_concurrency = fields.Int()
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([OutputBindingStr, NestedField(OutputSchema)], allow_none=True),
    )

    @pre_load
    def load_items(self, data, **kwargs):  # pylint: disable= unused-argument
        # load items from json to convert the assets in it to rest
        try:
            items = data["items"]
            if isinstance(items, str):
                items = json.loads(items)
            data["items"] = items
        except Exception:  # pylint: disable=W0718
            pass
        return data

    @pre_dump
    def convert_control_flow_body_to_binding_str(self, data, **kwargs):  # pylint: disable= unused-argument
        return super(ParallelForSchema, self).convert_control_flow_body_to_binding_str(data, **kwargs)

    @pre_dump
    def resolve_outputs(self, job, **kwargs):  # pylint: disable=unused-argument
        result = copy.copy(job)
        _resolve_outputs(result, job)
        return result

    @pre_dump
    def serialize_items(self, data, **kwargs):  # pylint: disable= unused-argument
        # serialize items to json string to avoid being removed by _dump_for_validation
        from azure.ai.ml.entities._job.pipeline._io import InputOutputBase

        def _binding_handler(obj):
            if isinstance(obj, InputOutputBase):
                return str(obj)
            return repr(obj)

        result = copy.copy(data)
        if isinstance(result.items, (dict, list)):
            # use str to serialize input/output builder
            result._items = json.dumps(result.items, default=_binding_handler)
        return result


class FLScatterGatherSchema(ControlFlowSchema):
    # TODO determine serialization, or if this is actually needed

    # @pre_dump
    def serialize_items(self, data, **kwargs):
        pass

    # @pre_dump
    def resolve_outputs(self, job, **kwargs):
        pass
