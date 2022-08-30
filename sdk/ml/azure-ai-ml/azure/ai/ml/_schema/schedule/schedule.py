# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields

from azure.ai.ml._schema.core.fields import ArmStr, NestedField, UnionField
from azure.ai.ml._schema.core.resource import ResourceSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml._schema.schedule.create_job import CreateJobFileRefField, PipelineCreateJobSchema
from azure.ai.ml._schema.schedule.trigger import CronTriggerSchema, RecurrenceTriggerSchema
from azure.ai.ml.constants import AzureMLResourceType


class ScheduleSchema(ResourceSchema):
    name = fields.Str(attribute="name", required=True)
    display_name = fields.Str(attribute="display_name")
    trigger = UnionField(
        [
            NestedField(CronTriggerSchema),
            NestedField(RecurrenceTriggerSchema),
        ],
    )
    create_job = UnionField(
        [
            ArmStr(azureml_type=AzureMLResourceType.JOB),
            CreateJobFileRefField,
            NestedField(PipelineCreateJobSchema),
        ]
    )
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    is_enabled = fields.Boolean(dump_only=True)
    provisioning_state = fields.Str(dump_only=True)
