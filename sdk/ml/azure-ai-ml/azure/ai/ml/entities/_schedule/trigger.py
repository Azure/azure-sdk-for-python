# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
import logging
from abc import ABC
from datetime import datetime
from typing import List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import CronTrigger as RestCronTrigger
from azure.ai.ml._restclient.v2023_04_01_preview.models import RecurrenceSchedule as RestRecurrencePattern
from azure.ai.ml._restclient.v2023_04_01_preview.models import RecurrenceTrigger as RestRecurrenceTrigger
from azure.ai.ml._restclient.v2023_04_01_preview.models import TriggerBase as RestTriggerBase
from azure.ai.ml._restclient.v2023_04_01_preview.models import TriggerType as RestTriggerType
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml.constants import TimeZone
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class TriggerBase(RestTranslatableMixin, ABC):
    """Base class of Trigger.

    :param type: Trigger Type
    :type type: str
    :param start_time: Specifies start time of schedule in ISO 8601 format.
    :type start_time: Union[str, datetime]
    :param end_time: Specifies end time of schedule in ISO 8601 format.
        Note that end_time is not supported for compute schedules.
    :type end_time: Union[str, datetime]
    :param time_zone: Time zone in which the schedule runs. Default to UTC(+00:00).
        This does apply to the start_time and end_time.
    :type time_zone: Optional[TimeZone]
    """

    def __init__(
        self,
        *,
        type: str,  # pylint: disable=redefined-builtin
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        time_zone: TimeZone = TimeZone.UTC,
    ):
        super().__init__()
        self.type = type
        self.start_time = start_time
        self.end_time = end_time
        self.time_zone = time_zone

    @classmethod
    def _from_rest_object(cls, obj: RestTriggerBase) -> Union["CronTrigger", "RecurrenceTrigger"]:
        if obj.trigger_type == RestTriggerType.RECURRENCE:
            return RecurrenceTrigger._from_rest_object(obj)
        if obj.trigger_type == RestTriggerType.CRON:
            return CronTrigger._from_rest_object(obj)


class RecurrencePattern(RestTranslatableMixin):
    """Recurrence pattern.

    :param hours: List of hours for recurrence schedule pattern.
    :type hours: Union[int, List[int]]
    :param minutes: List of minutes for recurrence schedule pattern.
    :type minutes: Union[int, List[int]]
    :param week_days: List of weekdays for recurrence schedule pattern.
        Possible values include: "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    :type week_days: Union[str, List[str]]
    :param month_days: List of month days for recurrence schedule pattern.
    :type month_days: Union[int, List[int]]
    """

    def __init__(
        self,
        *,
        hours: Union[int, List[int]],
        minutes: Union[int, List[int]],
        week_days: Optional[Union[str, List[str]]] = None,
        month_days: Optional[Union[int, List[int]]] = None,
    ):
        self.hours = hours
        self.minutes = minutes
        self.week_days = week_days
        self.month_days = month_days

    def _to_rest_object(self) -> RestRecurrencePattern:
        return RestRecurrencePattern(
            hours=[self.hours] if not isinstance(self.hours, list) else self.hours,
            minutes=[self.minutes] if not isinstance(self.minutes, list) else self.minutes,
            week_days=[self.week_days] if self.week_days and not isinstance(self.week_days, list) else self.week_days,
            month_days=[self.month_days]
            if self.month_days and not isinstance(self.month_days, list)
            else self.month_days,
        )

    def _to_rest_compute_pattern_object(self) -> RestRecurrencePattern:
        # This function is added because we can't make compute trigger to use same class
        # with schedule from service side.
        if self.month_days:
            module_logger.warning("'month_days' is ignored for not supported on compute recurrence schedule.")
        return RestRecurrencePattern(
            hours=[self.hours] if not isinstance(self.hours, list) else self.hours,
            minutes=[self.minutes] if not isinstance(self.minutes, list) else self.minutes,
            week_days=[self.week_days] if self.week_days and not isinstance(self.week_days, list) else self.week_days,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestRecurrencePattern) -> "RecurrencePattern":
        return cls(
            hours=obj.hours,
            minutes=obj.minutes,
            week_days=obj.week_days,
            month_days=obj.month_days if hasattr(obj, "month_days") else None,
        )


class CronTrigger(TriggerBase):
    """Cron Trigger.

    :param expression: Specifies cron expression of schedule.
        The expression should follow NCronTab format.
    :type expression: str
    :param start_time: Accepts str or datetime object. The tzinfo should be none if a datetime object, use
                       ``time_zone`` property to specify a time zone if needed. You can also specify this
                       parameter as a string in this format: YYYY-MM-DDThh:mm:ss. If None is provided, the
                       first workload is run instantly and the future workloads are run based on the schedule.
                       If the start time is in the past, the first workload is run at the next calculated run time.
    :type start_time: Union[str, datetime]
    :param end_time: Accepts str or datetime object. The tzinfo should be none if a datetime object, use
                     ``time_zone`` property to specify a time zone if needed. You can also specify this
                     parameter as a string in this format: YYYY-MM-DDThh:mm:ss. End time in the past is invalid
                     and will raise exception when creating schedule.
                     Note that end_time is not supported for compute schedules.
    :type end_time: Union[str, datetime]
    :param time_zone: Time zone in which the schedule runs. Default to UTC(+00:00).
        This does apply to the start_time and end_time.
    :type time_zone: Optional[TimeZone]
    """

    def __init__(
        self,
        *,
        expression: str,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        time_zone: Union[str, TimeZone] = TimeZone.UTC,
    ):
        super().__init__(
            type=RestTriggerType.CRON,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
        )
        self.expression = expression

    def _to_rest_object(self) -> RestCronTrigger:  # v2022_12_01.models.CronTrigger
        return RestCronTrigger(
            trigger_type=self.type,
            expression=self.expression,
            start_time=self.start_time,
            end_time=self.end_time,
            time_zone=self.time_zone,
        )

    def _to_rest_compute_cron_object(self) -> RestCronTrigger:  # v2022_12_01_preview.models.CronTrigger
        # This function is added because we can't make compute trigger to use same class
        # with schedule from service side.
        if self.end_time:
            module_logger.warning("'end_time' is ignored for not supported on compute schedule.")
        return RestCronTrigger(
            expression=self.expression,
            start_time=self.start_time,
            time_zone=self.time_zone,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestCronTrigger) -> "CronTrigger":
        return cls(
            expression=obj.expression,
            start_time=obj.start_time,
            end_time=obj.end_time,
            time_zone=obj.time_zone,
        )


class RecurrenceTrigger(TriggerBase):
    """Recurrence trigger.

    :param start_time: Specifies start time of schedule in ISO 8601 format.
    :type start_time: Union[str, datetime]
    :param end_time: Specifies end time of schedule in ISO 8601 format.
        Note that end_time is not supported for compute schedules.
    :type end_time: Union[str, datetime]
    :param time_zone: Time zone in which the schedule runs. Default to UTC(+00:00).
        This does apply to the start_time and end_time.
    :param frequency: Specifies frequency which to trigger schedule with.
     Possible values include: "minute", "hour", "day", "week", "month".
    :type frequency: str
    :param interval: Specifies schedule interval in conjunction with frequency.
    :type interval: int
    :param schedule: Specifies the recurrence schedule.
    :type schedule: RecurrencePattern
    """

    def __init__(
        self,
        *,
        frequency: str,
        interval: int,
        schedule: Optional[RecurrencePattern] = None,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        time_zone: Union[str, TimeZone] = TimeZone.UTC,
    ):
        super().__init__(
            type=RestTriggerType.RECURRENCE,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
        )
        # Create empty pattern as schedule is required in rest model
        self.schedule = schedule if schedule else RecurrencePattern(hours=[], minutes=[])
        self.frequency = frequency
        self.interval = interval

    def _to_rest_object(self) -> RestRecurrenceTrigger:  # v2022_12_01.models.RecurrenceTrigger
        return RestRecurrenceTrigger(
            frequency=snake_to_camel(self.frequency),
            interval=self.interval,
            schedule=self.schedule._to_rest_object(),
            start_time=self.start_time,
            end_time=self.end_time,
            time_zone=self.time_zone,
        )

    def _to_rest_compute_recurrence_object(self) -> RestRecurrenceTrigger:
        # v2022_12_01_preview.models.RecurrenceTrigger
        # This function is added because we can't make compute trigger to use same class
        # with schedule from service side.
        if self.end_time:
            module_logger.warning("'end_time' is ignored for not supported on compute schedule.")
        return RestRecurrenceTrigger(
            frequency=snake_to_camel(self.frequency),
            interval=self.interval,
            schedule=self.schedule._to_rest_compute_pattern_object(),
            start_time=self.start_time,
            time_zone=self.time_zone,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestRecurrenceTrigger) -> "RecurrenceTrigger":
        return cls(
            frequency=camel_to_snake(obj.frequency),
            interval=obj.interval,
            schedule=RecurrencePattern._from_rest_object(obj.schedule) if obj.schedule else None,
            start_time=obj.start_time,
            end_time=obj.end_time,
            time_zone=obj.time_zone,
        )
