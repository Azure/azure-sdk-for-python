# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from copy import deepcopy

import yaml
from marshmallow import INCLUDE, fields, post_load

from ...constants._common import BASE_PATH_CONTEXT_KEY
from ...constants._component import ComponentSource, NodeType
from ..assets.asset import AnonymousAssetSchema
from ..core.fields import FileRefField, NestedField, StringTransformedEnum
from ..job import ParameterizedParallelSchema
from .component import ComponentSchema
from .resource import ComponentResourceSchema
from .retry_settings import RetrySettingsSchema


class ParallelComponentSchema(ComponentSchema, ParameterizedParallelSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.PARALLEL], required=True)
    resources = NestedField(ComponentResourceSchema, unknown=INCLUDE)

    retry_settings = NestedField(RetrySettingsSchema, unknown=INCLUDE)


class RestParallelComponentSchema(ParallelComponentSchema):
    """When component load from rest, won't validate on name since there might be existing component with invalid
    name."""

    name = fields.Str(required=True)


class AnonymousParallelComponentSchema(AnonymousAssetSchema, ParallelComponentSchema):
    """Anonymous parallel component schema.

    Note inheritance follows order: AnonymousAssetSchema, ParallelComponentSchema because we need name and version to be
    dump_only(marshmallow collects fields follows method resolution order).
    """

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._component.parallel_component import ParallelComponent

        return ParallelComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            _source=kwargs.pop("_source", ComponentSource.YAML_JOB),
            **data,
        )


class ParallelComponentFileRefField(FileRefField):
    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)
        source_path = self.context[BASE_PATH_CONTEXT_KEY] / value

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = source_path.parent
        # pylint: disable=no-member
        component = AnonymousParallelComponentSchema(context=component_schema_context).load(
            component_dict, unknown=INCLUDE
        )
        component._source_path = source_path
        component._source = ComponentSource.YAML_COMPONENT
        return component
