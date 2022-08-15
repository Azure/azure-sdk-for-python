# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._restclient.v2022_01_01_preview.models import ComputePowerAction, DaysOfWeek, RecurrenceFrequency
from azure.ai.ml._restclient.v2022_01_01_preview.models import ScheduleStatus as ScheduleState
from azure.ai.ml._restclient.v2022_01_01_preview.models import TriggerType
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class BaseTriggerSchema(metaclass=PatchedSchemaMeta):
    start_time = fields.Str()
    time_zone = fields.Str()


class CronTriggerSchema(BaseTriggerSchema):
    type = StringTransformedEnum(required=True, allowed_values=TriggerType.CRON)
    expression = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import CronTrigger

        data.pop("type")
        return CronTrigger(**data)


class RecurrenceScheduleSchema(metaclass=PatchedSchemaMeta):
    week_days = fields.List(
        StringTransformedEnum(
            allowed_values=[
                DaysOfWeek.Sunday,
                DaysOfWeek.Monday,
                DaysOfWeek.Tuesday,
                DaysOfWeek.Wednesday,
                DaysOfWeek.Thursday,
                DaysOfWeek.Friday,
                DaysOfWeek.Saturday,
            ],
        )
    )
    hours = fields.List(fields.Int())
    minutes = fields.List(fields.Int())


class RecurrenceTriggerSchema(BaseTriggerSchema):
    type = StringTransformedEnum(required=True, allowed_values=TriggerType.RECURRENCE)
    frequency = StringTransformedEnum(
        required=True,
        allowed_values=[
            RecurrenceFrequency.SECOND,
            RecurrenceFrequency.MINUTE,
            RecurrenceFrequency.HOUR,
            RecurrenceFrequency.DAY,
            RecurrenceFrequency.WEEK,
            RecurrenceFrequency.MONTH,
        ],
    )
    interval = fields.Int()
    schedule = NestedField(RecurrenceScheduleSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import RecurrenceTrigger

        data.pop("type")
        return RecurrenceTrigger(**data)


class ComputeStartStopScheduleSchema(metaclass=PatchedSchemaMeta):
    trigger = UnionField(
        [
            NestedField(CronTriggerSchema()),
            NestedField(RecurrenceTriggerSchema()),
        ],
    )
    action = StringTransformedEnum(
        required=True,
        allowed_values=[
            ComputePowerAction.START,
            ComputePowerAction.STOP,
        ],
    )
    state = StringTransformedEnum(
        allowed_values=[
            ScheduleState.ENABLED,
            ScheduleState.DISABLED,
        ],
    )
    schedule_id = fields.Str(dump_only=True)
    provisioning_state = fields.Str(dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ComputeStartStopSchedule

        return ComputeStartStopSchedule(**data)


class ComputeSchedulesSchema(metaclass=PatchedSchemaMeta):
    compute_start_stop = fields.List(NestedField(ComputeStartStopScheduleSchema))

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ComputeSchedules

        return ComputeSchedules(**data)
