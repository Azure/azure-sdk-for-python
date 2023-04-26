# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os.path

import pydash
from marshmallow import EXCLUDE, INCLUDE, fields, post_dump, pre_load

from ..._schema import AnonymousEnvironmentSchema, NestedField, StringTransformedEnum, UnionField
from ..._schema.component.component import ComponentSchema
from ..._schema.core.fields import ArmVersionedStr, CodeField, RegistryStr
from ..._schema.job.parameterized_spark import SparkConfSchema, SparkEntryClassSchema, SparkEntryFileSchema
from ..._utils._arm_id_utils import parse_name_label
from ..._utils.utils import get_valid_dot_keys_with_wildcard
from ...constants._common import LABELLED_RESOURCE_NAME, SOURCE_PATH_CONTEXT_KEY, AzureMLResourceType
from ...constants._component import NodeType as PublicNodeType
from .._utils import yaml_safe_load_with_base_resolver
from .environment import InternalEnvironmentSchema
from .input_output import (
    InternalEnumParameterSchema,
    InternalInputPortSchema,
    InternalOutputPortSchema,
    InternalParameterSchema,
    InternalPrimitiveOutputSchema,
)


class NodeType:
    COMMAND = "CommandComponent"
    DATA_TRANSFER = "DataTransferComponent"
    DISTRIBUTED = "DistributedComponent"
    HDI = "HDInsightComponent"
    PARALLEL = "ParallelComponent"
    SCOPE = "ScopeComponent"
    STARLITE = "StarliteComponent"
    SWEEP = "SweepComponent"
    PIPELINE = "PipelineComponent"
    HEMERA = "HemeraComponent"
    AE365EXEPOOL = "AE365ExePoolComponent"
    IPP = "IntellectualPropertyProtectedComponent"
    # internal spake component got a type value conflict with spark component
    # this enum is used to identify its create_function in factories
    SPARK = "DummySpark"

    @classmethod
    def all_values(cls):
        all_values = []
        for key, value in vars(cls).items():
            if not key.startswith("_") and isinstance(value, str):
                all_values.append(value)
        return all_values


class InternalComponentSchema(ComponentSchema):
    class Meta:
        unknown = INCLUDE

    # override name as 1p components allow . in name, which is not allowed in v2 components
    name = fields.Str()

    # override to allow empty properties
    tags = fields.Dict(keys=fields.Str())

    # override inputs & outputs to support 1P inputs & outputs, may need to do strict validation later
    # no need to check io type match since server will do that
    inputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(InternalParameterSchema),
                NestedField(InternalEnumParameterSchema),
                NestedField(InternalInputPortSchema),
            ]
        ),
    )
    # support primitive output for all internal components for now
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(InternalPrimitiveOutputSchema, unknown=EXCLUDE),
                NestedField(InternalOutputPortSchema, unknown=EXCLUDE),
            ]
        ),
    )

    # type field is required for registration
    type = StringTransformedEnum(
        allowed_values=NodeType.all_values(),
        casing_transform=lambda x: parse_name_label(x)[0],
        pass_original=True,
    )

    # need to resolve as it can be a local field
    code = CodeField()

    environment = UnionField(
        [
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            NestedField(InternalEnvironmentSchema),
        ]
    )

    def get_skip_fields(self):  # pylint: disable=no-self-use
        return ["properties"]

    def _serialize(self, obj, *, many: bool = False):
        # pylint: disable=no-member
        if many and obj is not None:
            return super(InternalComponentSchema, self)._serialize(obj, many=many)
        ret = super(InternalComponentSchema, self)._serialize(obj)
        for attr_name in obj.__dict__.keys():
            if (
                not attr_name.startswith("_")
                and attr_name not in self.get_skip_fields()
                and attr_name not in self.dump_fields
            ):
                ret[attr_name] = self.get_attribute(obj, attr_name, None)
        return ret

    # override param_override to ensure that param override happens after reloading the yaml
    @pre_load
    def add_param_overrides(self, data, **kwargs):
        source_path = self.context.pop(SOURCE_PATH_CONTEXT_KEY, None)
        if isinstance(data, dict) and source_path and os.path.isfile(source_path):

            def should_node_overwritten(_root, _parts):
                parts = _parts.copy()
                parts.pop()
                parts.append("type")
                _input_type = pydash.get(_root, parts, None)
                return isinstance(_input_type, str) and _input_type.lower() not in ["boolean"]

            # do override here
            with open(source_path, "r") as f:
                origin_data = yaml_safe_load_with_base_resolver(f)
                for dot_key_wildcard, condition_func in [
                    ("version", None),
                    ("inputs.*.default", should_node_overwritten),
                    ("inputs.*.enum", should_node_overwritten),
                ]:
                    for dot_key in get_valid_dot_keys_with_wildcard(
                        origin_data, dot_key_wildcard, validate_func=condition_func
                    ):
                        pydash.set_(data, dot_key, pydash.get(origin_data, dot_key))
        return super().add_param_overrides(data, **kwargs)

    @post_dump(pass_original=True)
    def simplify_input_output_port(self, data, original, **kwargs):  # pylint:disable=unused-argument, no-self-use
        # remove None in input & output
        for io_ports in [data["inputs"], data["outputs"]]:
            for port_name, port_definition in io_ports.items():
                io_ports[port_name] = dict(filter(lambda item: item[1] is not None, port_definition.items()))

        # hack, to match current serialization match expectation
        for port_name, port_definition in data["inputs"].items():
            if "mode" in port_definition:
                del port_definition["mode"]

        return data

    @post_dump(pass_original=True)
    def add_back_type_label(self, data, original, **kwargs):  # pylint:disable=unused-argument, no-self-use
        type_label = original._type_label  # pylint:disable=protected-access
        if type_label:
            data["type"] = LABELLED_RESOURCE_NAME.format(data["type"], type_label)
        return data


class InternalSparkComponentSchema(InternalComponentSchema):
    # type field is required for registration
    type = StringTransformedEnum(
        allowed_values=PublicNodeType.SPARK,
        casing_transform=lambda x: parse_name_label(x)[0].lower(),
        pass_original=True,
    )

    environment = UnionField(
        [
            # unlike other internal component, internal spark component do not use internal environment schema
            NestedField(AnonymousEnvironmentSchema),
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
            NestedField(InternalEnvironmentSchema),
        ],
        allow_none=True,
    )

    jars = UnionField(
        [
            fields.List(fields.Str()),
            fields.Str(),
        ],
    )
    py_files = UnionField(
        [
            fields.List(fields.Str()),
            fields.Str(),
        ],
        data_key="pyFiles",
        attribute="py_files",
    )

    entry = UnionField(
        [NestedField(SparkEntryFileSchema), NestedField(SparkEntryClassSchema)],
        required=True,
        metadata={"description": "Entry."},
    )

    files = fields.List(fields.Str(required=True))
    archives = fields.List(fields.Str(required=True))
    conf = NestedField(SparkConfSchema, unknown=INCLUDE)
    args = fields.Str(metadata={"description": "Command Line arguments."})
