# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,protected-access,no-member

from copy import deepcopy

import yaml
from marshmallow import INCLUDE, fields, post_load

from azure.ai.ml._schema.assets.asset import AnonymousAssetSchema
from azure.ai.ml._schema.component.component import ComponentSchema
from azure.ai.ml._schema.core.fields import FileRefField, StringTransformedEnum
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._component import ComponentSource, NodeType

from ..job.parameterized_spark import ParameterizedSparkSchema


class SparkComponentSchema(ComponentSchema, ParameterizedSparkSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.SPARK])


class RestSparkComponentSchema(SparkComponentSchema):
    """When component load from rest, won't validate on name since there might
    be existing component with invalid name."""

    name = fields.Str(required=True)


class AnonymousSparkComponentSchema(AnonymousAssetSchema, SparkComponentSchema):
    """Anonymous spark component schema.

    Note inheritance follows order: AnonymousAssetSchema,
    SparkComponentSchema because we need name and version to be
    dump_only(marshmallow collects fields follows method resolution
    order).
    """

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._component.spark_component import SparkComponent

        # Inline component will have source=YAML.JOB
        # As we only regard full separate component file as YAML.COMPONENT
        return SparkComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            _source=kwargs.pop("_source", ComponentSource.YAML_JOB),
            **data,
        )


class SparkComponentFileRefField(FileRefField):
    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)
        source_path = self.context[BASE_PATH_CONTEXT_KEY] / value

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = source_path.parent
        component = AnonymousSparkComponentSchema(context=component_schema_context).load(
            component_dict, unknown=INCLUDE
        )
        component._source_path = source_path
        component._source = ComponentSource.YAML_COMPONENT
        return component
