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

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword type: The type of trigger.
    :paramtype type: str
    :keyword start_time: Specifies the start time of the schedule in ISO 8601 format.
    :paramtype start_time: Optional[Union[str, datetime]]
    :keyword end_time: Specifies the end time of the schedule in ISO 8601 format.
        Note that end_time is not supported for compute schedules.
    :paramtype end_time: Optional[Union[str, datetime]]
    :keyword time_zone: The time zone where the schedule will run. Defaults to UTC(+00:00).
        Note that this applies to the start_time and end_time.
    :paramtype time_zone: ~azure.ai.ml.constants.TimeZone
    """

    def __init__(
        self,
        *,
        type: str,  # pylint: disable=redefined-builtin
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        time_zone: Union[str, TimeZone] = TimeZone.UTC,
    ) -> None:
        super().__init__()
        self.type = type
        self.start_time = start_time
        self.end_time = end_time
        self.time_zone = time_zone

    @classmethod
    def _from_rest_object(cls, obj: RestTriggerBase) -> Optional[Union["CronTrigger", "RecurrenceTrigger"]]:
        if obj.trigger_type == RestTriggerType.RECURRENCE:
            return RecurrenceTrigger._from_rest_object(obj)
        if obj.trigger_type == RestTriggerType.CRON:
            return CronTrigger._from_rest_object(obj)

        return None


class RecurrencePattern(RestTranslatableMixin):
    """Recurrence pattern for a job schedule.

    :keyword hours: The number of hours for the recurrence schedule pattern.
    :paramtype hours: Union[int, List[int]]
    :keyword minutes: The number of minutes for the recurrence schedule pattern.
    :paramtype minutes: Union[int, List[int]]
    :keyword week_days: A list of days of the week for the recurrence schedule pattern.
        Acceptable values include: "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    :type week_days: Optional[Union[str, List[str]]]
    :keyword month_days: A list of days of the month for the recurrence schedule pattern.
    :paramtype month_days: Optional[Union[int, List[int]]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START job_schedule_configuration]
            :end-before: [END job_schedule_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a JobSchedule to use a RecurrencePattern.
    """

    def __init__(
        self,
        *,
        hours: Union[int, List[int]],
        minutes: Union[int, List[int]],
        week_days: Optional[Union[str, List[str]]] = None,
        month_days: Optional[Union[int, List[int]]] = None,
    ) -> None:
        self.hours = hours
        self.minutes = minutes
        self.week_days = week_days
        self.month_days = month_days

    def _to_rest_object(self) -> RestRecurrencePattern:
        return RestRecurrencePattern(
            hours=[self.hours] if not isinstance(self.hours, list) else self.hours,
            minutes=[self.minutes] if not isinstance(self.minutes, list) else self.minutes,
            week_days=[self.week_days] if self.week_days and not isinstance(self.week_days, list) else self.week_days,
            month_days=(
                [self.month_days] if self.month_days and not isinstance(self.month_days, list) else self.month_days
            ),
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
    """Cron Trigger for a job schedule.

    :keyword expression: The cron expression of schedule, following NCronTab format.
    :paramtype expression: str
    :keyword start_time: The start time for the trigger. If using a datetime object, leave the tzinfo as None and use
        the ``time_zone`` parameter to specify a time zone if needed. If using a string, use the format
        YYYY-MM-DDThh:mm:ss. Defaults to running the first workload instantly and continuing future workloads
        based on the schedule. If the start time is in the past, the first workload is run at the next calculated run
        time.
    :paramtype start_time: Optional[Union[str, datetime]]
    :keyword end_time: The start time for the trigger. If using a datetime object, leave the tzinfo as None and use
        the ``time_zone`` parameter to specify a time zone if needed. If using a string, use the format
        YYYY-MM-DDThh:mm:ss. Note that end_time is not supported for compute schedules.
    :paramtype end_time: Optional[Union[str, datetime]]
    :keyword time_zone: The time zone where the schedule will run. Defaults to UTC(+00:00).
        Note that this applies to the start_time and end_time.
    :paramtype time_zone: Union[str, ~azure.ai.ml.constants.TimeZone]
    :raises Exception: Raised if end_time is in the past.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START cron_trigger_configuration]
            :end-before: [END cron_trigger_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a CronTrigger.
    """

    def __init__(
        self,
        *,
        expression: str,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        time_zone: Union[str, TimeZone] = TimeZone.UTC,
    ) -> None:
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
    """Recurrence trigger for a job schedule.

    :keyword start_time: Specifies the start time of the schedule in ISO 8601 format.
    :paramtype start_time: Optional[Union[str, datetime]]
    :keyword end_time: Specifies the end time of the schedule in ISO 8601 format.
        Note that end_time is not supported for compute schedules.
    :paramtype end_time: Optional[Union[str, datetime]]
    :keyword time_zone: The time zone where the schedule will run. Defaults to UTC(+00:00).
        Note that this applies to the start_time and end_time.
    :paramtype time_zone: Union[str, ~azure.ai.ml.constants.TimeZone]
    :keyword frequency: Specifies the frequency that the schedule should be triggered with.
     Possible values include: "minute", "hour", "day", "week", "month".
    :type frequency: str
    :keyword interval: Specifies the interval in conjunction with the frequency that the schedule should be triggered
        with.
    :paramtype interval: int
    :keyword schedule: Specifies the recurrence pattern.
    :paramtype schedule: Optional[~azure.ai.ml.entities.RecurrencePattern]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START job_schedule_configuration]
            :end-before: [END job_schedule_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a JobSchedule to trigger recurrence every 4 weeks.
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
    ) -> None:
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
