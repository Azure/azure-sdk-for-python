# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import INCLUDE, fields, post_dump
from marshmallow.error_store import ErrorStore

from azure.ai.ml._schema import ArmVersionedStr, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.component.component import ComponentSchema
from azure.ai.ml._schema.core.fields import LocalPathField, RegistryStr, SerializeValidatedUrl
from azure.ai.ml.constants import AzureMLResourceType

from .input_output import (
    InternalEnumParameterSchema,
    InternalInputPortSchema,
    InternalOutputPortSchema,
    InternalParameterSchema,
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

    @classmethod
    def all_values(cls):
        all_values = []
        for key, value in vars(cls).items():
            if not key.startswith("_") and isinstance(value, str):
                all_values.append(value)
        return all_values


class InternalBaseComponentSchema(ComponentSchema):
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
    outputs = fields.Dict(keys=fields.Str(), values=NestedField(InternalOutputPortSchema))

    # type field is required for registration
    type = StringTransformedEnum(allowed_values=NodeType.all_values(), casing_transform=lambda x: x)

    # need to resolve as it can be a local field
    code = UnionField(
        [
            SerializeValidatedUrl(),
            LocalPathField(),
            RegistryStr(azureml_type=AzureMLResourceType.CODE),
            # put arm versioned string at last order as it can deserialize any string into "azureml:<origin>"
            ArmVersionedStr(azureml_type=AzureMLResourceType.CODE),
        ],
        metadata={"description": "A local path or http:, https:, azureml: url pointing to a remote location."},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_skip_fields(self):
        return ["properties"]

    def _serialize(self, obj, *, many: bool = False):
        if many and obj is not None:
            return super(InternalBaseComponentSchema, self)._serialize(obj, many=many)
        ret = super(InternalBaseComponentSchema, self)._serialize(obj)
        for attr_name, value_to_serialize in obj.__dict__.items():
            if (
                not attr_name.startswith("_")
                and attr_name not in self.get_skip_fields()
                and attr_name not in self.dump_fields
            ):
                ret[attr_name] = self.get_attribute(obj, attr_name, None)
        return ret

    def _deserialize(
        self,
        data,
        *,
        error_store: ErrorStore,
        many: bool = False,
        partial=False,
        unknown=INCLUDE,
        index=None,
    ):
        return super(InternalBaseComponentSchema, self)._deserialize(
            data,
            error_store=error_store,
            many=many,
            partial=partial,
            unknown=unknown,
            index=index,
        )

    @post_dump(pass_original=True)
    def simplify_input_output_port(self, data, original, **kwargs):
        # remove None in input & output
        for io_ports in [data["inputs"], data["outputs"]]:
            for port_name, port_definition in io_ports.items():
                io_ports[port_name] = dict(filter(lambda item: item[1] is not None, port_definition.items()))

        # hack, to match current serialization match expectation
        for port_name, port_definition in data["inputs"].items():
            if "default" in port_definition:
                data["inputs"][port_name]["default"] = original.inputs[port_name].default
            if "mode" in port_definition:
                del port_definition["mode"]

        return data
