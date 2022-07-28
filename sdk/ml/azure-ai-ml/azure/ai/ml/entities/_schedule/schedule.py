# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC
from typing import List, Union

from azure.ai.ml.constants import TimeZone
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ScheduleBase as RestScheduleBase,
    CronSchedule as RestCronSchedule,
    RecurrenceSchedule as RestRecurrenceSchedule,
    RecurrencePattern as RestRecurrencePattern,
    ScheduleType as RestScheduleType,
)
from azure.ai.ml.entities._util import SnakeToPascalDescriptor, LiteralToListDescriptor


class Schedule(ABC):

    status = SnakeToPascalDescriptor("schedule_status")
    type = SnakeToPascalDescriptor("schedule_type")

    def __init__(self):
        pass

    @classmethod
    def _from_rest_object(cls, obj: RestScheduleBase) -> "Schedule":
        if obj.schedule_type == RestScheduleType.CRON:
            return CronSchedule._from_rest_object(obj)
        if obj.schedule_type == RestScheduleType.RECURRENCE:
            return RecurrenceSchedule._from_rest_object(obj)


class RecurrencePattern(RestRecurrencePattern):
    """Recurrence pattern

    :param hours: List of hours for recurrence schedule pattern.
    :type hours: Union[int, List[int]]
    :param minutes: List of minutes for recurrence schedule pattern.
    :type minutes: Union[int, List[int]]
    :param weekdays: List of weekdays for recurrence schedule pattern.
    :type weekdays: Union[str, List[str]]
    """

    hours = LiteralToListDescriptor()
    minutes = LiteralToListDescriptor()
    weekdays = LiteralToListDescriptor()

    def __init__(
        self,
        *,
        hours: Union[int, List[int]],
        minutes: Union[int, List[int]],
        weekdays: Union[str, List[str]] = None,
    ):
        super().__init__(hours=hours, minutes=minutes, weekdays=weekdays)

    @classmethod
    def _from_rest_object(cls, obj: RestRecurrencePattern) -> "RecurrencePattern":
        return cls(
            hours=obj.hours,
            minutes=obj.minutes,
            weekdays=obj.weekdays,
        )


class CronSchedule(RestCronSchedule, Schedule):
    """Cron schedule

    :param status: Specifies the schedule's status. Possible values include: "enabled",
        "disabled".
    :type status: str
    :param start_time: Specifies start time of schedule in ISO 8601 format. If no time zone
        offset is specified in the start_time, it will default to UTC (+0:00)
    :type start_time: Union[str, datetime]
    :param end_time: Specifies end time of schedule in ISO 8601 format. If no time zone
        offset is specified in the end_time, it will default to UTC (+0:00)
    :type end_time: Union[str, datetime]
    :param time_zone: Time zone in which the schedule runs. This does not apply to the start_time and end_time.
    :type time_zone: Optional[TimeZone]
    :param expression: Specifies cron expression of schedule.
        The expression should follow NCronTab format.
    :type expression: str
    """

    def __init__(
        self,
        *,
        expression: str,
        status: str = None,
        start_time: str = None,
        end_time: str = None,
        time_zone: TimeZone = TimeZone.UTC,
    ):
        super().__init__(
            expression=expression, schedule_status=status, start_time=start_time, end_time=end_time, time_zone=time_zone
        )

    @classmethod
    def _from_rest_object(cls, obj: RestCronSchedule) -> "CronSchedule":
        return cls(
            expression=obj.expression,
            status=obj.schedule_status,
            start_time=obj.start_time,
            end_time=obj.end_time,
            time_zone=obj.time_zone,
        )


class RecurrenceSchedule(RestRecurrenceSchedule, Schedule):
    """Recurrence schedule

    :param status: Specifies the schedule's status. Possible values include: "enabled",
        "disabled".
    :type status: str
    :param start_time: Specifies start time of schedule in ISO 8601 format. If no time zone
        offset is specified in the start_time, it will default to UTC (+0:00)
    :type start_time: Union[str, datetime]
    :param end_time: Specifies end time of schedule in ISO 8601 format. If no time zone
        offset is specified in the end_time, it will default to UTC (+0:00)
    :type end_time: Union[str, datetime]
    :param time_zone: Time zone in which the schedule runs. This does not apply to the start_time and end_time.
    :type time_zone: Optional[TimeZone]
    :param frequency: Specifies frequency which to trigger schedule with.
     Possible values include: "minute", "hour", "day", "week", "month".
    :type frequency: str
    :param interval: Specifies schedule interval in conjunction with frequency.
    :type interval: int
    :param pattern: Specifies the recurrence schedule pattern.
    :type pattern: RecurrencePattern
    """

    frequency = SnakeToPascalDescriptor()

    def __init__(
        self,
        *,
        frequency: str,
        interval: int,
        pattern: RecurrencePattern = None,
        status: str = None,
        start_time: str = None,
        end_time: str = None,
        time_zone: TimeZone = TimeZone.UTC,
    ):
        super().__init__(
            frequency=frequency,
            interval=interval,
            pattern=pattern,
            schedule_status=status,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestRecurrenceSchedule) -> "RecurrenceSchedule":
        return cls(
            frequency=obj.frequency,
            interval=obj.interval,
            pattern=RecurrencePattern._from_rest_object(obj.pattern) if obj.pattern else None,
            status=obj.schedule_status,
            start_time=obj.start_time,
            end_time=obj.end_time,
            time_zone=obj.time_zone,
        )
