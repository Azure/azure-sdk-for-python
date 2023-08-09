# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from copy import deepcopy

import yaml
from marshmallow import INCLUDE, fields, post_load

from azure.ai.ml._schema.assets.asset import AnonymousAssetSchema
from azure.ai.ml._schema.component.component import ComponentSchema
from azure.ai.ml._schema.component.parallel_task import ComponentParallelTaskSchema
from azure.ai.ml._schema.component.resource import ComponentResourceSchema
from azure.ai.ml._schema.component.retry_settings import RetrySettingsSchema
from azure.ai.ml._schema.core.fields import DumpableEnumField, FileRefField, NestedField, StringTransformedEnum
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, LoggingLevel
from azure.ai.ml.constants._component import ComponentSource, NodeType


class ParallelComponentSchema(ComponentSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.PARALLEL], required=True)
    resources = NestedField(ComponentResourceSchema, unknown=INCLUDE)
    logging_level = DumpableEnumField(
        allowed_values=[LoggingLevel.DEBUG, LoggingLevel.INFO, LoggingLevel.WARN],
        dump_default=LoggingLevel.INFO,
        metadata={
            "description": "A string of the logging level name, which is defined in 'logging'. \
            Possible values are 'WARNING', 'INFO', and 'DEBUG'."
        },
    )
    task = NestedField(ComponentParallelTaskSchema, unknown=INCLUDE)
    mini_batch_size = fields.Str(
        metadata={"description": "The The batch size of current job."},
    )
    partition_keys = fields.List(
        fields.Str(), metadata={"description": "The keys used to partition input data into mini-batches"}
    )

    input_data = fields.Str()
    retry_settings = NestedField(RetrySettingsSchema, unknown=INCLUDE)
    max_concurrency_per_instance = fields.Integer(
        dump_default=1,
        metadata={"description": "The max parallellism that each compute instance has."},
    )
    error_threshold = fields.Integer(
        dump_default=-1,
        metadata={
            "description": "The number of item processing failures should be ignored. \
            If the error_threshold is reached, the job terminates. \
            For a list of files as inputs, one item means one file reference. \
            This setting doesn't apply to command parallelization."
        },
    )
    mini_batch_error_threshold = fields.Integer(
        dump_default=-1,
        metadata={
            "description": "The number of mini batch processing failures should be ignored. \
            If the mini_batch_error_threshold is reached, the job terminates. \
            For a list of files as inputs, one item means one file reference. \
            This setting can be used by either command or python function parallelization. \
            Only one error_threshold setting can be used in one job."
        },
    )


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
