# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,protected-access,no-member

from marshmallow import fields

from azure.ai.ml._schema import YamlFileSchema
from azure.ai.ml._schema.component import ComponentSchema
from azure.ai.ml._schema.component.component import ComponentNameStr
from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    LocalPathField,
    NestedField,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._component import NodeType


class ConnectionSchema(metaclass=PatchedSchemaMeta):
    connection = fields.Str()
    deployment_name = fields.Str()


class ComponentMetadataSchema(metaclass=PatchedSchemaMeta):
    name = ComponentNameStr()
    version = fields.Str()
    display_name = fields.Str()
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    is_deterministic = fields.Bool()


class FlowComponentArgumentSchema(metaclass=PatchedSchemaMeta):
    variant = fields.Str()
    column_mappings = fields.Dict(
        fields.Str(),
        fields.Str(),
    )
    connections = fields.Dict(
        keys=fields.Str(),
        values=NestedField(ConnectionSchema),
    )
    environment_variables = fields.Dict(
        fields.Str(),
        fields.Str(),
    )


class FlowSchema(YamlFileSchema, ComponentMetadataSchema):
    additional_includes = fields.List(LocalPathField())


class RunSchema(YamlFileSchema, ComponentMetadataSchema, FlowComponentArgumentSchema):
    flow = LocalPathField(required=True)


class FlowComponentSchema(ComponentSchema, FlowComponentArgumentSchema):
    """
    FlowSchema and FlowRunSchema are used to load flow while FlowComponentSchema is used to dump flow.
    """

    class Meta:
        exclude = ["inputs", "outputs"]  # component doesn't have inputs & outputs

    type = StringTransformedEnum(allowed_values=[NodeType.FLOW_PARALLEL], required=True)

    # name, version, tags, display_name and is_deterministic are inherited from ComponentSchema
    properties = fields.Dict(
        fields.Str(),
        fields.Str(),
    )

    # this is different from regular CodeField
    code = UnionField(
        [
            LocalPathField(),
            ArmVersionedStr(azureml_type=AzureMLResourceType.CODE),
        ],
        metadata={"description": "A local path or http:, https:, azureml: url pointing to a remote location."},
    )
    additional_includes = fields.List(LocalPathField(), load_only=True)
