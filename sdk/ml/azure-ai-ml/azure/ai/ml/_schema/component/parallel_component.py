# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from email.policy import default
import os.path

import yaml
from copy import deepcopy
from marshmallow import fields, post_load, INCLUDE, post_dump

from azure.ai.ml._schema import (
    StringTransformedEnum,
    NestedField,
)
from azure.ai.ml._schema.core.fields import FileRefField
from azure.ai.ml._schema.assets.asset import AnonymousAssetSchema
from azure.ai.ml._schema.component.component import BaseComponentSchema
from azure.ai.ml._schema.component.resource import ComponentResourceSchema
from azure.ai.ml._schema.component.retry_settings import RetrySettingsSchema
from azure.ai.ml._schema.component.parallel_task import ComponentParallelTaskSchema

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, NodeType, LoggingLevel


class ParallelComponentSchema(BaseComponentSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.PARALLEL], required=True)
    resources = NestedField(ComponentResourceSchema, unknown=INCLUDE)
    logging_level = StringTransformedEnum(
        allowed_values=[LoggingLevel.DEBUG, LoggingLevel.INFO, LoggingLevel.WARN],
        casing_transform=lambda *args: None,
        default=LoggingLevel.INFO,
        metadata={
            "description": "A string of the logging level name, which is defined in 'logging'. Possible values are 'WARNING', 'INFO', and 'DEBUG'."
        },
    )
    task = NestedField(ComponentParallelTaskSchema, unknown=INCLUDE)
    mini_batch_size = fields.Str(
        metadata={"description": "The The batch size of current job."},
    )
    input_data = fields.Str()
    retry_settings = NestedField(RetrySettingsSchema, unknown=INCLUDE)
    max_concurrency_per_instance = fields.Integer(
        default=1,
        metadata={"description": "The max parallellism that each compute instance has."},
    )
    error_threshold = fields.Integer(
        default=-1,
        metadata={
            "description": "The number of item processing failures should be ignored. If the error_threshold is reached, the job terminates. For a list of files as inputs, one item means one file reference. This setting doesn't apply to command parallelization."
        },
    )
    mini_batch_error_threshold = fields.Integer(
        default=-1,
        metadata={
            "description": "The number of mini batch processing failures should be ignored. If the mini_batch_error_threshold is reached, the job terminates. For a list of files as inputs, one item means one file reference. This setting can be used by either command or python function parallelization. Only one error_threshold setting can be used in one job."
        },
    )


class RestParallelComponentSchema(ParallelComponentSchema):
    """
    When component load from rest, won't validate on name since there might be existing component with invalid name.
    """

    name = fields.Str(required=True)


class AnonymousParallelComponentSchema(AnonymousAssetSchema, ParallelComponentSchema):
    """Anonymous parallel component schema.

    Note inheritance follows order: AnonymousAssetSchema, ParallelComponentSchema because we need name and version to
    be dump only(marshmallow collects fields follows method resolution order).
    """

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ParallelComponent

        return ParallelComponent(
            base_path=self.context[BASE_PATH_CONTEXT_KEY],
            **data,
        )


class ParallelComponentFileRefField(FileRefField):
    def _deserialize(self, value, attr, data, **kwargs):
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        component_dict = yaml.safe_load(data)

        # Update base_path to parent path of component file.
        component_schema_context = deepcopy(self.context)
        component_schema_context[BASE_PATH_CONTEXT_KEY] = (self.context[BASE_PATH_CONTEXT_KEY] / value).parent
        return AnonymousParallelComponentSchema(context=component_schema_context).load(component_dict, unknown=INCLUDE)
