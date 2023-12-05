# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging

from marshmallow import INCLUDE, ValidationError, fields, post_dump, post_load, pre_dump, validates

from ..._schema.component import (
    AnonymousCommandComponentSchema,
    AnonymousDataTransferCopyComponentSchema,
    AnonymousImportComponentSchema,
    AnonymousParallelComponentSchema,
    AnonymousSparkComponentSchema,
    ComponentFileRefField,
    ComponentYamlRefField,
    DataTransferCopyComponentFileRefField,
    ImportComponentFileRefField,
    ParallelComponentFileRefField,
    SparkComponentFileRefField,
)
from ..._utils.utils import is_data_binding_expression
from ...constants._common import AzureMLResourceType
from ...constants._component import DataTransferTaskType, NodeType
from ...entities._inputs_outputs import Input
from ...entities._job.pipeline._attr_dict import _AttrDict
from ...exceptions import ValidationException
from .._sweep.parameterized_sweep import ParameterizedSweepSchema
from .._utils.data_binding_expression import support_data_binding_expression_for_fields
from ..component.flow import FlowComponentSchema
from ..core.fields import (
    ArmVersionedStr,
    ComputeField,
    EnvironmentField,
    NestedField,
    RegistryStr,
    StringTransformedEnum,
    TypeSensitiveUnionField,
    UnionField,
)
from ..core.schema import PathAwareSchema
from ..job import ParameterizedCommandSchema, ParameterizedParallelSchema, ParameterizedSparkSchema
from ..job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from ..job.input_output_entry import DatabaseSchema, FileSystemSchema, OutputSchema
from ..job.input_output_fields_provider import InputsField
from ..job.job_limits import CommandJobLimitsSchema
from ..job.parameterized_spark import SparkEntryClassSchema, SparkEntryFileSchema
from ..job.services import (
    JobServiceSchema,
    JupyterLabJobServiceSchema,
    SshJobServiceSchema,
    TensorBoardJobServiceSchema,
    VsCodeJobServiceSchema,
)
from ..pipeline.pipeline_job_io import OutputBindingStr
from ..spark_resource_configuration import SparkResourceConfigurationForNodeSchema

module_logger = logging.getLogger(__name__)


# do inherit PathAwareSchema to support relative path & default partial load (allow None value if not specified)
class BaseNodeSchema(PathAwareSchema):
    """Base schema for all node schemas."""

    unknown = INCLUDE

    inputs = InputsField(support_databinding=True)
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([OutputBindingStr, NestedField(OutputSchema)], allow_none=True),
    )
    properties = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))
    comment = fields.Str()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # data binding expression is not supported inside component field, while validation error
        # message will be very long when component is an object as error message will include
        # str(component), so just add component to skip list. The same to trial in Sweep.
        support_data_binding_expression_for_fields(self, ["type", "component", "trial", "inputs"])

    @post_dump(pass_original=True)
    # pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
    def add_user_setting_attr_dict(self, data, original_data, **kwargs):  # pylint: disable=unused-argument
        """Support serializing unknown fields for pipeline node."""
        if isinstance(original_data, _AttrDict):
            user_setting_attr_dict = original_data._get_attrs()
            # TODO: dump _AttrDict values to serializable data like dict instead of original object
            # skip fields that are already serialized
            for key, value in user_setting_attr_dict.items():
                if key not in data:
                    data[key] = value
        return data

    # an alternative would be set schema property to be load_only, but sub-schemas like CommandSchema usually also
    # inherit from other schema classes which also have schema property. Set post dump here would be more efficient.
    @post_dump()
    def remove_meaningless_key_for_node(
        self,
        data,
        **kwargs,  # pylint: disable=unused-argument
    ):
        data.pop("$schema", None)
        return data


def _delete_type_for_binding(io):
    for key in io:
        if isinstance(io[key], Input) and io[key].path and is_data_binding_expression(io[key].path):
            io[key].type = None


def _resolve_inputs(result, original_job):
    result._inputs = original_job._build_inputs()
    # delete type for literal binding input
    _delete_type_for_binding(result._inputs)


def _resolve_outputs(result, original_job):
    result._outputs = original_job._build_outputs()
    # delete type for literal binding output
    _delete_type_for_binding(result._outputs)


def _resolve_inputs_outputs(job):
    # Try resolve object's inputs & outputs and return a resolved new object
    import copy

    result = copy.copy(job)
    _resolve_inputs(result, job)
    _resolve_outputs(result, job)

    return result


class CommandSchema(BaseNodeSchema, ParameterizedCommandSchema):
    """Schema for Command."""

    # pylint: disable=unused-argument
    component = TypeSensitiveUnionField(
        {
            NodeType.COMMAND: [
                # inline component or component file reference starting with FILE prefix
                NestedField(AnonymousCommandComponentSchema, unknown=INCLUDE),
                # component file reference
                ComponentFileRefField(),
            ],
        },
        plain_union_fields=[
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
        ],
        required=True,
    )
    # code is directly linked to component.code, so no need to validate or dump it
    code = fields.Str(allow_none=True, load_only=True)
    type = StringTransformedEnum(allowed_values=[NodeType.COMMAND])
    compute = ComputeField()
    # do not promote it as CommandComponent has no field named 'limits'
    limits = NestedField(CommandJobLimitsSchema)
    # Change required fields to optional
    command = fields.Str(
        metadata={
            "description": "The command run and the parameters passed. \
            This string may contain place holders of inputs in {}. "
        },
        load_only=True,
    )
    environment = EnvironmentField()
    services = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(SshJobServiceSchema),
                NestedField(JupyterLabJobServiceSchema),
                NestedField(TensorBoardJobServiceSchema),
                NestedField(VsCodeJobServiceSchema),
                # JobServiceSchema should be the last in the list.
                # To support types not set by users like Custom, Tracking, Studio.
                NestedField(JobServiceSchema),
            ],
            is_strict=True,
        ),
    )
    identity = UnionField(
        [
            NestedField(ManagedIdentitySchema),
            NestedField(AMLTokenIdentitySchema),
            NestedField(UserIdentitySchema),
        ]
    )

    @post_load
    def make(self, data, **kwargs) -> "Command":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.command_func import command

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        try:
            command_node = command(**data)
        except ValidationException as e:
            # It may raise ValidationError during initialization, command._validate_io e.g. raise ValidationError
            # instead in marshmallow function, so it won't break SchemaValidatable._schema_validate
            raise ValidationError(e.message) from e
        return command_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class SweepSchema(BaseNodeSchema, ParameterizedSweepSchema):
    """Schema for Sweep."""

    # pylint: disable=unused-argument
    type = StringTransformedEnum(allowed_values=[NodeType.SWEEP])
    compute = ComputeField()
    trial = TypeSensitiveUnionField(
        {
            NodeType.SWEEP: [
                # inline component or component file reference starting with FILE prefix
                NestedField(AnonymousCommandComponentSchema, unknown=INCLUDE),
                # component file reference
                ComponentFileRefField(),
            ],
        },
        plain_union_fields=[
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
        ],
        required=True,
    )

    @post_load
    def make(self, data, **kwargs) -> "Sweep":
        from azure.ai.ml.entities._builders import Sweep, parse_inputs_outputs

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        return Sweep(**data)  # pylint: disable=abstract-class-instantiated

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class ParallelSchema(BaseNodeSchema, ParameterizedParallelSchema):
    """
    Schema for Parallel.
    """

    # pylint: disable=unused-argument
    compute = ComputeField()
    component = TypeSensitiveUnionField(
        {
            NodeType.PARALLEL: [
                # inline component or component file reference starting with FILE prefix
                NestedField(AnonymousParallelComponentSchema, unknown=INCLUDE),
                # component file reference
                ParallelComponentFileRefField(),
            ],
            NodeType.FLOW_PARALLEL: [
                NestedField(FlowComponentSchema, unknown=INCLUDE, dump_only=True),
                ComponentYamlRefField(),
            ],
        },
        plain_union_fields=[
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
        ],
        required=True,
    )
    identity = UnionField(
        [
            NestedField(ManagedIdentitySchema),
            NestedField(AMLTokenIdentitySchema),
            NestedField(UserIdentitySchema),
        ]
    )
    type = StringTransformedEnum(allowed_values=[NodeType.PARALLEL])

    @post_load
    def make(self, data, **kwargs) -> "Parallel":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.parallel_func import parallel_run_function

        data = parse_inputs_outputs(data)
        parallel_node = parallel_run_function(**data)
        return parallel_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class ImportSchema(BaseNodeSchema):
    """
    Schema for Import.
    """

    # pylint: disable=unused-argument
    component = TypeSensitiveUnionField(
        {
            NodeType.IMPORT: [
                # inline component or component file reference starting with FILE prefix
                NestedField(AnonymousImportComponentSchema, unknown=INCLUDE),
                # component file reference
                ImportComponentFileRefField(),
            ],
        },
        plain_union_fields=[
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
        ],
        required=True,
    )
    type = StringTransformedEnum(allowed_values=[NodeType.IMPORT])

    @post_load
    def make(self, data, **kwargs) -> "Import":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.import_func import import_job

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        import_node = import_job(**data)
        return import_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class SparkSchema(BaseNodeSchema, ParameterizedSparkSchema):
    """
    Schema for Spark.
    """

    # pylint: disable=unused-argument
    component = TypeSensitiveUnionField(
        {
            NodeType.SPARK: [
                # inline component or component file reference starting with FILE prefix
                NestedField(AnonymousSparkComponentSchema, unknown=INCLUDE),
                # component file reference
                SparkComponentFileRefField(),
            ],
        },
        plain_union_fields=[
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
        ],
        required=True,
    )
    type = StringTransformedEnum(allowed_values=[NodeType.SPARK])
    compute = ComputeField()
    resources = NestedField(SparkResourceConfigurationForNodeSchema)
    entry = UnionField(
        [NestedField(SparkEntryFileSchema), NestedField(SparkEntryClassSchema)],
        metadata={"description": "Entry."},
    )
    py_files = fields.List(fields.Str())
    jars = fields.List(fields.Str())
    files = fields.List(fields.Str())
    archives = fields.List(fields.Str())
    identity = UnionField(
        [
            NestedField(ManagedIdentitySchema),
            NestedField(AMLTokenIdentitySchema),
            NestedField(UserIdentitySchema),
        ]
    )

    # code is directly linked to component.code, so no need to validate or dump it
    code = fields.Str(allow_none=True, load_only=True)

    @post_load
    def make(self, data, **kwargs) -> "Spark":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.spark_func import spark

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        try:
            spark_node = spark(**data)
        except ValidationException as e:
            # It may raise ValidationError during initialization, command._validate_io e.g. raise ValidationError
            # instead in marshmallow function, so it won't break SchemaValidatable._schema_validate
            raise ValidationError(e.message) from e
        return spark_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class DataTransferCopySchema(BaseNodeSchema):
    """
    Schema for DataTransferCopy.
    """

    # pylint: disable=unused-argument
    component = TypeSensitiveUnionField(
        {
            NodeType.DATA_TRANSFER: [
                # inline component or component file reference starting with FILE prefix
                NestedField(AnonymousDataTransferCopyComponentSchema, unknown=INCLUDE),
                # component file reference
                DataTransferCopyComponentFileRefField(),
            ],
        },
        plain_union_fields=[
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
        ],
        required=True,
    )
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.COPY_DATA], required=True)
    type = StringTransformedEnum(allowed_values=[NodeType.DATA_TRANSFER], required=True)
    compute = ComputeField()

    @post_load
    def make(self, data, **kwargs) -> "DataTransferCopy":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.data_transfer_func import copy_data

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        try:
            data_transfer_node = copy_data(**data)
        except ValidationException as e:
            # It may raise ValidationError during initialization, data_transfer._validate_io e.g. raise ValidationError
            # instead in marshmallow function, so it won't break SchemaValidatable._schema_validate
            raise ValidationError(e.message) from e
        return data_transfer_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class DataTransferImportSchema(BaseNodeSchema):
    # pylint: disable=unused-argument
    component = UnionField(
        [
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
        ],
        required=True,
    )
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.IMPORT_DATA], required=True)
    type = StringTransformedEnum(allowed_values=[NodeType.DATA_TRANSFER], required=True)
    compute = ComputeField()
    source = UnionField([NestedField(DatabaseSchema), NestedField(FileSystemSchema)], required=True, allow_none=False)
    outputs = fields.Dict(
        keys=fields.Str(), values=UnionField([OutputBindingStr, NestedField(OutputSchema)]), allow_none=False
    )

    @validates("inputs")
    def inputs_key(self, value):
        raise ValidationError(f"inputs field is not a valid filed in task type " f"{DataTransferTaskType.IMPORT_DATA}.")

    @validates("outputs")
    def outputs_key(self, value):
        if len(value) != 1 or list(value.keys())[0] != "sink":
            raise ValidationError(
                f"outputs field only support one output called sink in task type "
                f"{DataTransferTaskType.IMPORT_DATA}."
            )

    @post_load
    def make(self, data, **kwargs) -> "DataTransferImport":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.data_transfer_func import import_data

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        try:
            data_transfer_node = import_data(**data)
        except ValidationException as e:
            # It may raise ValidationError during initialization, data_transfer._validate_io e.g. raise ValidationError
            # instead in marshmallow function, so it won't break SchemaValidatable._schema_validate
            raise ValidationError(e.message) from e
        return data_transfer_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)


class DataTransferExportSchema(BaseNodeSchema):
    # pylint: disable=unused-argument
    component = UnionField(
        [
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
        ],
        required=True,
    )
    task = StringTransformedEnum(allowed_values=[DataTransferTaskType.EXPORT_DATA])
    type = StringTransformedEnum(allowed_values=[NodeType.DATA_TRANSFER])
    compute = ComputeField()
    inputs = InputsField(support_databinding=True, allow_none=False)
    sink = UnionField([NestedField(DatabaseSchema), NestedField(FileSystemSchema)], required=True, allow_none=False)

    @validates("inputs")
    def inputs_key(self, value):
        if len(value) != 1 or list(value.keys())[0] != "source":
            raise ValidationError(
                f"inputs field only support one input called source in task type "
                f"{DataTransferTaskType.EXPORT_DATA}."
            )

    @validates("outputs")
    def outputs_key(self, value):
        raise ValidationError(
            f"outputs field is not a valid filed in task type " f"{DataTransferTaskType.EXPORT_DATA}."
        )

    @post_load
    def make(self, data, **kwargs) -> "DataTransferExport":
        from azure.ai.ml.entities._builders import parse_inputs_outputs
        from azure.ai.ml.entities._builders.data_transfer_func import export_data

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        try:
            data_transfer_node = export_data(**data)
        except ValidationException as e:
            # It may raise ValidationError during initialization, data_transfer._validate_io e.g. raise ValidationError
            # instead in marshmallow function, so it won't break SchemaValidatable._schema_validate
            raise ValidationError(e.message) from e
        return data_transfer_node

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)
