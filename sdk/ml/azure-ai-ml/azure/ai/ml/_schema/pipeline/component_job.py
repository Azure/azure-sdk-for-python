# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from email.policy import default
import logging
from marshmallow import fields, post_load, INCLUDE, Schema, pre_dump, pre_load

from azure.ai.ml.constants import AzureMLResourceType
from azure.ai.ml.constants import NodeType
from azure.ai.ml._schema import (
    ArmVersionedStr,
    NestedField,
    UnionField,
    AnonymousEnvironmentSchema,
    RegistryStr,
    PathAwareSchema,
)

from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._schema.component import (
    AnonymousCommandComponentSchema,
    AnonymousParallelComponentSchema,
    ComponentFileRefField,
    ParallelComponentFileRefField,
)
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField
from azure.ai.ml._schema.job.input_output_entry import OutputSchema
from azure.ai.ml._schema.pipeline.pipeline_job_io import OutputBindingStr
from .._sweep.parameterized_sweep import ParameterizedSweepSchema
from .._utils.data_binding_expression import support_data_binding_expression_for_fields

from ..core.fields import ComputeField, StringTransformedEnum
from ..job import ParameterizedCommandSchema, ParameterizedParallelSchema
from ..job.distribution import PyTorchDistributionSchema, TensorFlowDistributionSchema, MPIDistributionSchema
from ..job.job_limits import CommandJobLimitsSchema

module_logger = logging.getLogger(__name__)


# do inherit PathAwareSchema to support relative path & default partial load (allow None value if not specified)
class BaseNodeSchema(PathAwareSchema):
    unknown = INCLUDE

    compute = ComputeField()
    inputs = InputsField()
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([OutputBindingStr, NestedField(OutputSchema)], allow_none=True),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        support_data_binding_expression_for_fields(self, ["type"])


def _delete_type_for_binding(io):
    for key in io:
        if isinstance(io[key], Input) and io[key].path and is_data_binding_expression(io[key].path):
            io[key].type = None


def _resolve_inputs_outputs(job):
    # Try resolve object's inputs & outputs and return a resolved new object
    import copy

    result = copy.copy(job)
    result._inputs = job._build_inputs()
    # delete type for literal binding input
    _delete_type_for_binding(result._inputs)

    result._outputs = job._build_outputs()
    # delete type for literal binding output
    _delete_type_for_binding(result._outputs)
    return result


class CommandSchema(BaseNodeSchema, ParameterizedCommandSchema):
    component = UnionField(
        [
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
            # inline component or component file reference starting with FILE prefix
            NestedField(AnonymousCommandComponentSchema, unknown=INCLUDE),
            # component file reference
            ComponentFileRefField(),
        ],
        required=True,
    )
    type = StringTransformedEnum(allowed_values=[NodeType.COMMAND])
    # do not promote it as CommandComponent has no field named 'limits'
    limits = NestedField(CommandJobLimitsSchema)
    # Change required fields to optional
    command = fields.Str(
        metadata={
            "description": "The command run and the parameters passed. This string may contain place holders of inputs in {}. "
        }
    )
    environment = UnionField(
        [
            NestedField(AnonymousEnvironmentSchema),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
        ],
    )

    @post_load
    def make(self, data, **kwargs) -> "Command":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.command_func import command
        from azure.ai.ml.constants import ComponentSource

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        command_node = command(**data)
        return command_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class SweepSchema(BaseNodeSchema, ParameterizedSweepSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.SWEEP])
    trial = UnionField(
        [
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
            # inline component or component file reference starting with FILE prefix
            NestedField(AnonymousCommandComponentSchema, unknown=INCLUDE),
            # component file reference
            ComponentFileRefField(),
        ],
        required=True,
    )

    @post_load
    def make(self, data, **kwargs) -> "Sweep":
        from azure.ai.ml.entities._builders import (
            Sweep,
            parse_inputs_outputs,
        )

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        return Sweep(**data)

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class ParallelSchema(BaseNodeSchema, ParameterizedParallelSchema):
    component = UnionField(
        [
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
            # inline component or component file reference starting with FILE prefix
            NestedField(AnonymousParallelComponentSchema, unknown=INCLUDE),
            # component file reference
            ParallelComponentFileRefField(),
        ],
        required=True,
    )
    type = StringTransformedEnum(allowed_values=[NodeType.PARALLEL])

    @post_load
    def make(self, data, **kwargs) -> "Parallel":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.parallel_func import parallel

        data = parse_inputs_outputs(data)
        parallel_node = parallel(**data)
        return parallel_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)
