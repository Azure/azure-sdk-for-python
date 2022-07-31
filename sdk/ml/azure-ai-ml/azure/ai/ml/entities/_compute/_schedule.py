# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Optional, List
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    Recurrence,
    Cron,
    RecurrenceSchedule,
    RecurrenceFrequency,
    ScheduleStatus as ScheduleState,
    TriggerType,
    ComputePowerAction,
    ComputeSchedules as RestComputeSchedules,
    ComputeStartStopSchedule as RestComputeStartStopSchedule,
)
from azure.ai.ml.constants import TYPE
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental


class BaseTrigger(ABC):
    """Base class for trigger, can't be instantiated directly.

    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(self, **kwargs):
        self._type = kwargs.pop("type", None)

    @property
    def type(self) -> Optional[str]:
        """Type of the schedule trigger.

        :return: Type of the schedule trigger.
        :rtype: str
        """
        return self._type


class CronTrigger(BaseTrigger, Cron):
    """Cron trigger

    :param start_time: The start time.
    :type start_time: str
    :param time_zone: The time zone.
    :type time_zone: str
    :param expression: The cron expression.
    :type expression: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(self, *, start_time: str = None, time_zone: str = None, expression: str = None, **kwargs):
        kwargs[TYPE] = TriggerType.CRON
        super().__init__(**kwargs)

        self.start_time = start_time
        self.time_zone = time_zone
        self.expression = expression


class RecurrenceTrigger(BaseTrigger, Recurrence):
    """Recurrence trigger

    :param start_time: The start time.
    :type start_time: str
    :param time_zone: The time zone.
    :type time_zone: str
    :param frequency: Frequency of the recurrence trigger.
    :type frequency: RecurrenceFrequency
    :param interval: Recurrence interval.
    :type interval: int
    :param schedule: Schedule of the recurrence trigger.
    :type schedule: RecurrenceSchedule
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        start_time: str = None,
        time_zone: str = None,
        frequency: RecurrenceFrequency = None,
        interval: int = None,
        schedule: RecurrenceSchedule = None,
        **kwargs
    ):
        kwargs[TYPE] = TriggerType.RECURRENCE
        super().__init__(**kwargs)

        self.start_time = start_time
        self.time_zone = time_zone
        self.frequency = frequency
        self.interval = interval
        self.schedule = schedule


class ComputeStartStopSchedule(RestTranslatableMixin):
    """Schedules for compute start or stop scenario

    :param trigger: The trigger of the schedule.
    :type trigger: Trigger
    :param action: The compute power action.
    :type action: ComputePowerAction
    :param state: The state of the schedule.
    :type state: ScheduleState
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        trigger: BaseTrigger = None,
        action: ComputePowerAction = None,
        state: ScheduleState = ScheduleState.ENABLED,
        **kwargs
    ):
        self.trigger = trigger
        self.action = action
        self.state = state
        self._schedule_id = kwargs.pop("schedule_id", None)
        self._provisioning_state = kwargs.pop("provisioning_state", None)

    @property
    def schedule_id(self) -> Optional[str]:
        """Schedule id, readonly

        :return: Schedule id.
        :rtype: Optional[str]
        """
        return self._schedule_id

    @property
    def provisioning_state(self) -> Optional[str]:
        """Schedule provisioning state, readonly

        :return: Schedule provisioning state.
        :rtype: Optional[str]
        """
        return self._provisioning_state

    def _to_rest_object(self) -> RestComputeStartStopSchedule:
        rest_object = RestComputeStartStopSchedule(
            action=self.action,
            status=self.state,
        )

        if isinstance(self.trigger, CronTrigger):
            rest_object.trigger_type = TriggerType.CRON
            rest_object.cron = self.trigger
        elif isinstance(self.trigger, RecurrenceTrigger):
            rest_object.trigger_type = TriggerType.RECURRENCE
            rest_object.recurrence = self.trigger

        return rest_object

    @classmethod
    def _from_rest_object(cls, rest_obj: RestComputeStartStopSchedule) -> "ComputeStartStopSchedule":
        schedule = ComputeStartStopSchedule(
            action=rest_obj.action,
            state=rest_obj.status,
            schedule_id=rest_obj.id,
            provisioning_state=rest_obj.provisioning_status,
        )

        if rest_obj.trigger_type == TriggerType.Cron:
            schedule.trigger = CronTrigger(
                start_time=rest_obj.cron.start_time,
                time_zone=rest_obj.cron.time_zone,
                expression=rest_obj.cron.expression,
            )
        elif rest_obj.trigger_type == TriggerType.Recurrence:
            schedule.trigger = RecurrenceTrigger(
                start_time=rest_obj.recurrence.start_time,
                time_zone=rest_obj.recurrence.time_zone,
                frequency=rest_obj.recurrence.frequency,
                interval=rest_obj.recurrence.interval,
                schedule=rest_obj.recurrence.schedule,
            )

        return schedule


@experimental
class ComputeSchedules(RestTranslatableMixin):
    """Compute schedules

    :param compute_start_stop: Compute start or stop schedules.
    :type compute_start_stop: List[ComputeStartStopSchedule]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(self, *, compute_start_stop: List[ComputeStartStopSchedule] = None, **kwargs):
        self.compute_start_stop = compute_start_stop

    def _to_rest_object(self) -> RestComputeSchedules:
        rest_schedules: List[RestComputeStartStopSchedule] = []
        if self.compute_start_stop:
            for schedule in self.compute_start_stop:
                rest_schedules.append(schedule._to_rest_object())

        return RestComputeSchedules(
            compute_start_stop=rest_schedules,
        )

    @classmethod
    def _from_rest_object(cls, rest_obj: RestComputeSchedules) -> "ComputeSchedules":
        schedules: List[ComputeStartStopSchedule] = []
        if rest_obj.compute_start_stop:
            for schedule in rest_obj.compute_start_stop:
                schedules.append(ComputeStartStopSchedule._from_rest_object(schedule))

        return ComputeSchedules(
            compute_start_stop=schedules,
        )
