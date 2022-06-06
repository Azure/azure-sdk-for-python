# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema import NestedField, PathAwareSchema, StringTransformedEnum
from marshmallow import fields, INCLUDE
from azure.ai.ml.constants import LoggingLevel
from azure.ai.ml._schema.component.parallel_task import ComponentParallelTaskSchema
from azure.ai.ml._schema.resource_configuration import ResourceConfigurationSchema
from azure.ai.ml._schema.component.retry_settings import RetrySettingsSchema


class ParameterizedParallelSchema(PathAwareSchema):
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
        metadata={"description": "The batch size of current job."},
    )
    input_data = fields.Str()
    resources = NestedField(ResourceConfigurationSchema)
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
    environment_variables = fields.Dict(keys=fields.Str(), values=fields.Str())
