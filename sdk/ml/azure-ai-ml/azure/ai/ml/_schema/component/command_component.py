# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access,no-member

from copy import deepcopy

import yaml
from marshmallow import INCLUDE, fields, post_dump, post_load

from azure.ai.ml._schema.assets.asset import AnonymousAssetSchema
from azure.ai.ml._schema.component.component import ComponentSchema
from azure.ai.ml._schema.component.input_output import (
    OutputPortSchema,
    PrimitiveOutputSchema,
)
from azure.ai.ml._schema.component.resource import ComponentResourceSchema
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import (
    ExperimentalField,
    FileRefField,
    NestedField,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml._schema.job.distribution import (
    MPIDistributionSchema,
    PyTorchDistributionSchema,
    TensorFlowDistributionSchema,
    RayDistributionSchema,
)
from azure.ai.ml._schema.job.parameterized_command import ParameterizedCommandSchema
from azure.ai.ml._utils.utils import is_private_preview_enabled
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AzureDevopsArtifactsType
from azure.ai.ml.constants._component import ComponentSource, NodeType


class AzureDevopsArtifactsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=[AzureDevopsArtifactsType.ARTIFACT])
    feed = fields.Str()
    name = fields.Str()
    version = fields.Str()
    scope = fields.Str()
    organization = fields.Str()
    project = fields.Str()


class CommandComponentSchema(ComponentSchema, ParameterizedCommandSchema):
    class Meta:
        exclude = ["environment_variables"]  # component doesn't have environment variables

    type = StringTransformedEnum(allowed_values=[NodeType.COMMAND])
    resources = NestedField(ComponentResourceSchema, unknown=INCLUDE)
    distribution = UnionField(
        [
            NestedField(MPIDistributionSchema, unknown=INCLUDE),
            NestedField(TensorFlowDistributionSchema, unknown=INCLUDE),
            NestedField(PyTorchDistributionSchema, unknown=INCLUDE),
            ExperimentalField(NestedField(RayDistributionSchema, unknown=INCLUDE)),
        ],
        metadata={"description": "Provides the configuration for a distributed run."},
    )
    # primitive output is only supported for command component & pipeline component
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(OutputPortSchema),
                NestedField(PrimitiveOutputSchema, unknown=INCLUDE),
            ]
        ),
    )
    properties = fields.Dict(keys=fields.Str(), values=fields.Raw())

    # Note: AzureDevopsArtifactsSchema only available when private preview flag opened before init of command component
    # schema class.
    if is_private_preview_enabled():
        additional_includes = fields.List(UnionField([fields.Str(), NestedField(AzureDevopsArtifactsSchema)]))
    else:
        additional_includes = fields.List(fields.Str())

    @post_dump
    def remove_unnecessary_fields(self, component_schema_dict, **kwargs):
        # remove empty properties to keep the component spec unchanged
        if not component_schema_dict.get("properties"):
            component_schema_dict.pop("properties", None)
        if (
            component_schema_dict.get("additional_includes") is not None
            and len(component_schema_dict["additional_includes"]) == 0
        ):
            component_schema_dict.pop("additional_includes")
        return component_schema_dict


class RestCommandComponentSchema(CommandComponentSchema):
    """When component load from rest, won't validate on name since there might be existing component with invalid
    name."""

    name = fields.Str(required=True)


class AnonymousCommandComponentSchema(AnonymousAssetSchema, CommandComponentSchema):
    """Anonymous command component schema.

    Note inheritance follows order: AnonymousAssetSchema, CommandComponentSchema because we need name and version to be
    dump_only(marshmallow collects fields follows method resolution order).
    """

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import CommandComponent

        # Inline component will have source=YAML.JOB
        # As we only regard full separate component file as YAML.COMPONENT
        return CommandComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            _source=ComponentSource.YAML_JOB,
            **data,
        )


class ComponentFileRefField(FileRefField):
    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)
        source_path = self.context[BASE_PATH_CONTEXT_KEY] / value

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = source_path.parent
        component = AnonymousCommandComponentSchema(context=component_schema_context).load(
            component_dict, unknown=INCLUDE
        )
        component._source_path = source_path
        component._source = ComponentSource.YAML_COMPONENT
        return component
