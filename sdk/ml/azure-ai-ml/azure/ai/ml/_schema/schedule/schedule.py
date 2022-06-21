# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, pre_dump, post_load, validate, ValidationError, post_dump
from azure.ai.ml.constants import TimeZone
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import StringTransformedEnum, NestedField, UnionField, DumpableIntegerField
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ScheduleStatus,
    ScheduleType,
    RecurrenceFrequency,
    Weekday,
)


class ScheduleSchema(metaclass=PatchedSchemaMeta):
    status = StringTransformedEnum(allowed_values=[o.value for o in ScheduleStatus])
    start_time = fields.DateTime()
    time_zone = fields.Str(validate=validate.OneOf([o.value for o in TimeZone]))

    @post_dump(pass_original=True)
    def resolve_time_zone(self, data, original_data, **kwargs):
        """
        Auto-convert will get string like "TimeZone.UTC" for TimeZone enum object, while the valid result should be "UTC"
        """
        if isinstance(original_data.time_zone, TimeZone):
            data["time_zone"] = original_data.time_zone.value
        return data


class CronScheduleSchema(ScheduleSchema):
    type = StringTransformedEnum(allowed_values=ScheduleType.CRON, required=True)
    expression = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs) -> "CronSchedule":
        from azure.ai.ml.entities._schedule.schedule import CronSchedule

        data.pop("type")
        return CronSchedule(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._schedule.schedule import CronSchedule

        if not isinstance(data, CronSchedule):
            raise ValidationError("Cannot dump non-CronSchedule object into CronScheduleSchema")
        return data


class RecurrencePatternSchema(metaclass=PatchedSchemaMeta):
    hours = UnionField([DumpableIntegerField(), fields.List(fields.Int())], required=True)
    minutes = UnionField([DumpableIntegerField(), fields.List(fields.Int())], required=True)
    weekdays = UnionField(
        [
            StringTransformedEnum(allowed_values=[o.value for o in Weekday]),
            fields.List(StringTransformedEnum(allowed_values=[o.value for o in Weekday])),
        ]
    )

    @post_load
    def make(self, data, **kwargs) -> "RecurrencePattern":
        from azure.ai.ml.entities._schedule.schedule import RecurrencePattern

        return RecurrencePattern(**data)


class RecurrenceScheduleSchema(ScheduleSchema):
    type = StringTransformedEnum(allowed_values=ScheduleType.RECURRENCE, required=True)
    frequency = StringTransformedEnum(allowed_values=[o.value for o in RecurrenceFrequency], required=True)
    interval = fields.Int(required=True)
    pattern = NestedField(RecurrencePatternSchema())

    @post_load
    def make(self, data, **kwargs) -> "RecurrenceSchedule":
        from azure.ai.ml.entities._schedule.schedule import RecurrenceSchedule

        data.pop("type")
        return RecurrenceSchedule(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._schedule.schedule import RecurrenceSchedule

        if not isinstance(data, RecurrenceSchedule):
            raise ValidationError("Cannot dump non-RecurrenceSchedule object into RecurrenceScheduleSchema")
        return data
