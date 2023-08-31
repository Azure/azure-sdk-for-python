# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,protected-access,no-member

from marshmallow import fields

from azure.ai.ml._schema import YamlFileSchema
from azure.ai.ml._schema.component import ComponentSchema
from azure.ai.ml._schema.component.component import ComponentNameStr
from azure.ai.ml._schema.core.fields import ArmVersionedStr, LocalPathField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._component import NodeType


class _ComponentMetadataSchema(metaclass=PatchedSchemaMeta):
    """Schema to recognize metadata of a flow as a component."""

    name = ComponentNameStr()
    version = fields.Str()
    display_name = fields.Str()
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    is_deterministic = fields.Bool()


class _FlowAttributesSchema(metaclass=PatchedSchemaMeta):
    """Schema to recognize attributes of a flow."""

    variant = fields.Str()
    column_mappings = fields.Dict(
        fields.Str(),
        fields.Str(),
    )
    connections = fields.Dict(
        keys=fields.Str(),
        values=fields.Dict(
            keys=fields.Str(),
            values=fields.Str(),
        ),
    )
    environment_variables = fields.Dict(
        fields.Str(),
        fields.Str(),
    )


class FlowSchema(YamlFileSchema, _ComponentMetadataSchema):
    """Schema for flow.dag.yaml file."""

    additional_includes = fields.List(LocalPathField())


class RunSchema(YamlFileSchema, _ComponentMetadataSchema, _FlowAttributesSchema):
    """Schema for run.yaml file."""

    flow = LocalPathField(required=True)


class FlowComponentSchema(ComponentSchema, _FlowAttributesSchema):
    """FlowSchema and FlowRunSchema are used to load flow while FlowComponentSchema is used to dump flow."""

    class Meta:
        """Override this to exclude inputs & outputs as component doesn't have them."""

        exclude = ["inputs", "outputs"]  # component doesn't have inputs & outputs

    # TODO: name should be required?
    name = ComponentNameStr()

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
