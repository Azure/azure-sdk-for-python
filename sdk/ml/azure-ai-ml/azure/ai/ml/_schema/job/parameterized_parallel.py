# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import INCLUDE, fields

from azure.ai.ml._schema.component.parallel_task import ComponentParallelTaskSchema
from azure.ai.ml._schema.component.retry_settings import RetrySettingsSchema
from azure.ai.ml._schema.core.fields import DumpableEnumField, NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.job.input_output_entry import InputLiteralValueSchema
from azure.ai.ml._schema.job_resource_configuration import JobResourceConfigurationSchema
from azure.ai.ml.constants._common import LoggingLevel

from ..core.fields import UnionField


class ParameterizedParallelSchema(PathAwareSchema):
    logging_level = DumpableEnumField(
        allowed_values=[LoggingLevel.DEBUG, LoggingLevel.INFO, LoggingLevel.WARN],
        dump_default=LoggingLevel.INFO,
        metadata={
            "description": (
                "A string of the logging level name, which is defined in 'logging'. "
                "Possible values are 'WARNING', 'INFO', and 'DEBUG'."
            )
        },
    )
    task = NestedField(ComponentParallelTaskSchema, unknown=INCLUDE)
    mini_batch_size = fields.Str(
        metadata={"description": "The batch size of current job."},
    )
    partition_keys = fields.List(
        fields.Str(), metadata={"description": "The keys used to partition input data into mini-batches"}
    )
    input_data = fields.Str()
    resources = NestedField(JobResourceConfigurationSchema)
    retry_settings = NestedField(RetrySettingsSchema, unknown=INCLUDE)
    max_concurrency_per_instance = fields.Integer(
        dump_default=1,
        metadata={"description": "The max parallellism that each compute instance has."},
    )
    error_threshold = fields.Integer(
        dump_default=-1,
        metadata={
            "description": (
                "The number of item processing failures should be ignored. "
                "If the error_threshold is reached, the job terminates. "
                "For a list of files as inputs, one item means one file reference. "
                "This setting doesn't apply to command parallelization."
            )
        },
    )
    mini_batch_error_threshold = fields.Integer(
        dump_default=-1,
        metadata={
            "description": (
                "The number of mini batch processing failures should be ignored. "
                "If the mini_batch_error_threshold is reached, the job terminates. "
                "For a list of files as inputs, one item means one file reference. "
                "This setting can be used by either command or python function parallelization. "
                "Only one error_threshold setting can be used in one job."
            )
        },
    )
    environment_variables = UnionField(
        [
            fields.Dict(keys=fields.Str(), values=fields.Str()),
            # Used for binding environment variables
            NestedField(InputLiteralValueSchema),
        ]
    )
