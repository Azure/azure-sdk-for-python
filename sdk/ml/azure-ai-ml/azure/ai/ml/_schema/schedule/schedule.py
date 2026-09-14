# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.core.resource import ResourceSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml._schema.schedule.create_job import ScheduleCreateJobField
from azure.ai.ml._schema.schedule.trigger import CronTriggerSchema, RecurrenceTriggerSchema


class ScheduleSchema(ResourceSchema):
    name = fields.Str(attribute="name", required=True)
    display_name = fields.Str(attribute="display_name")
    trigger = UnionField(
        [
            NestedField(CronTriggerSchema),
            NestedField(RecurrenceTriggerSchema),
        ],
    )
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    is_enabled = fields.Boolean(dump_only=True)
    provisioning_state = fields.Str(dump_only=True)
    properties = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))


class JobScheduleSchema(ScheduleSchema):
    create_job = ScheduleCreateJobField()
