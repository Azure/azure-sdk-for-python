# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_dump, post_load

from azure.ai.ml._restclient.v2022_10_01_preview.models import RecurrenceFrequency, TriggerType, WeekDay
from azure.ai.ml._schema.core.fields import (
    DateTimeStr,
    DumpableIntegerField,
    NestedField,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants import TimeZone


class TriggerSchema(metaclass=PatchedSchemaMeta):
    start_time = UnionField([fields.DateTime(), DateTimeStr()])
    end_time = UnionField([fields.DateTime(), DateTimeStr()])
    time_zone = fields.Str()

    @post_dump(pass_original=True)
    # pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
    def resolve_time_zone(self, data, original_data, **kwargs):  # pylint: disable= unused-argument
        """
        Auto-convert will get string like "TimeZone.UTC" for TimeZone enum object,
        while the valid result should be "UTC"
        """
        if isinstance(original_data.time_zone, TimeZone):
            data["time_zone"] = original_data.time_zone.value
        return data


class CronTriggerSchema(TriggerSchema):
    type = StringTransformedEnum(allowed_values=TriggerType.CRON, required=True)
    expression = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs) -> "CronTrigger":  # pylint: disable= unused-argument
        from azure.ai.ml.entities import CronTrigger

        data.pop("type")
        return CronTrigger(**data)


class RecurrencePatternSchema(metaclass=PatchedSchemaMeta):
    hours = UnionField([DumpableIntegerField(), fields.List(fields.Int())], required=True)
    minutes = UnionField([DumpableIntegerField(), fields.List(fields.Int())], required=True)
    week_days = UnionField(
        [
            StringTransformedEnum(allowed_values=[o.value for o in WeekDay]),
            fields.List(StringTransformedEnum(allowed_values=[o.value for o in WeekDay])),
        ]
    )
    month_days = UnionField(
        [
            fields.Int(),
            fields.List(fields.Int()),
        ]
    )

    @post_load
    def make(self, data, **kwargs) -> "RecurrencePattern":  # pylint: disable= unused-argument
        from azure.ai.ml.entities import RecurrencePattern

        return RecurrencePattern(**data)


class RecurrenceTriggerSchema(TriggerSchema):
    type = StringTransformedEnum(allowed_values=TriggerType.RECURRENCE, required=True)
    frequency = StringTransformedEnum(allowed_values=[o.value for o in RecurrenceFrequency], required=True)
    interval = fields.Int(required=True)
    schedule = NestedField(RecurrencePatternSchema())

    @post_load
    def make(self, data, **kwargs) -> "RecurrenceTrigger":  # pylint: disable= unused-argument
        from azure.ai.ml.entities import RecurrenceTrigger

        data.pop("type")
        return RecurrenceTrigger(**data)
