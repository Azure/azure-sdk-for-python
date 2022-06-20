# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from email.policy import default
import logging
from pathlib import Path

from marshmallow import fields, post_load, INCLUDE, Schema, pre_dump, pre_load, post_dump, ValidationError

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
from ..._ml_exceptions import ValidationException
from ...entities._job.pipeline._attr_dict import _AttrDict

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

    @post_dump(pass_original=True)
    def add_user_setting_attr_dict(self, data, original_data, **kwargs):
        """Support serializing unknown fields for pipeline node."""
        if isinstance(original_data, _AttrDict):
            user_setting_attr_dict = original_data._get_attrs()
            data.update(user_setting_attr_dict)
        return data


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
        try:
            command_node = command(**data)
        except ValidationException as e:
            # It may raise ValidationError during initialization, command._validate_io e.g. raise ValidationError
            # instead in marshmallow function, so it won't break SchemaValidatable._schema_validate
            raise ValidationError(e.message)
        return command_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)

    @post_dump(pass_original=True)
    def resolve_code_path(self, data, original_data, **kwargs):
        # Command.code is relative to pipeline instead of Command.component after serialization,
        # so we need to transform it. Not sure if this is the best way to do it
        # maybe move this logic to LocalPathField
        if (
            hasattr(original_data.component, "code")
            and original_data.component.code is not None
            and original_data.component.base_path != original_data._base_path
        ):
            try:
                code_path = Path(original_data.component.base_path) / original_data.component.code
                if code_path.exists():
                    rebased_code_path = str(os.path.relpath(code_path, original_data._base_path))
                    data["code"], data["component"]["code"] = rebased_code_path, rebased_code_path
            except OSError:
                # OSError will be raised when _base_path or code is an arm_str or an invalid path,
                # then just return the origin value to avoid blocking serialization
                pass
        return data


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
