# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Optional, Union, cast

from azure.ai.ml._restclient.v2023_06_01_preview.models import CreateMonitorAction, RecurrenceFrequency
from azure.ai.ml._restclient.v2023_06_01_preview.models import Schedule as RestSchedule
from azure.ai.ml._restclient.v2023_06_01_preview.models import ScheduleProperties
from azure.ai.ml._schema.monitoring.schedule import MonitorScheduleSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, ScheduleType
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._monitoring.definition import MonitorDefinition
from azure.ai.ml.entities._schedule.schedule import Schedule
from azure.ai.ml.entities._schedule.trigger import CronTrigger, RecurrenceTrigger, TriggerBase
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict

module_logger = logging.getLogger(__name__)


class MonitorSchedule(Schedule, RestTranslatableMixin):
    """Monitor schedule.

    :keyword name: The schedule name.
    :paramtype name: str
    :keyword trigger: The schedule trigger.
    :paramtype trigger: Union[~azure.ai.ml.entities.CronTrigger, ~azure.ai.ml.entities.RecurrenceTrigger]
    :keyword create_monitor: The schedule action monitor definition.
    :paramtype create_monitor: ~azure.ai.ml.entities.MonitorDefinition
    :keyword display_name: The display name of the schedule.
    :paramtype display_name: Optional[str]
    :keyword description: A description of the schedule.
    :paramtype description: Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated.
    :paramtype tags: Optional[dict[str, str]]
    :keyword properties: The job property dictionary.
    :paramtype properties: Optional[dict[str, str]]
    """

    def __init__(
        self,
        *,
        name: str,
        trigger: Optional[Union[CronTrigger, RecurrenceTrigger]],
        create_monitor: MonitorDefinition,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name,
            trigger=trigger,
            display_name=display_name,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )
        self.create_monitor = create_monitor
        self._type = ScheduleType.MONITOR

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "MonitorSchedule":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return cls(
            base_path=cast(Dict, context[BASE_PATH_CONTEXT_KEY]),
            **load_from_dict(MonitorScheduleSchema, data, context, **kwargs),
        )

    def _to_rest_object(self) -> RestSchedule:
        if self.tags is not None:
            tags = {
                **self.tags,
            }
        # default data window size is calculated based on the trigger frequency
        # by default 7 days if user provides incorrect recurrence frequency
        # or a cron expression
        default_data_window_size = "P7D"
        ref_data_window_size = "P14D"
        if isinstance(self.trigger, RecurrenceTrigger):
            frequency = self.trigger.frequency.lower()
            interval = self.trigger.interval
            if frequency == RecurrenceFrequency.MINUTE.lower() or frequency == RecurrenceFrequency.HOUR.lower():
                default_data_window_size = "P1D"
                ref_data_window_size = "P2D"
            elif frequency == RecurrenceFrequency.DAY.lower():
                default_data_window_size = f"P{interval}D"
                ref_data_window_size = f"P{interval * 2}D"
            elif frequency == RecurrenceFrequency.WEEK.lower():
                default_data_window_size = f"P{interval * 7}D"
                ref_data_window_size = f"P{(interval * 7) * 2}D"
            elif frequency == RecurrenceFrequency.MONTH.lower():
                default_data_window_size = f"P{interval * 30}D"
                ref_data_window_size = f"P{(interval * 30) * 2}D"

        return RestSchedule(
            properties=ScheduleProperties(
                description=self.description,
                properties=self.properties,
                tags=tags,
                action=CreateMonitorAction(
                    monitor_definition=self.create_monitor._to_rest_object(
                        default_data_window_size=default_data_window_size, ref_data_window_size=ref_data_window_size
                    )
                ),
                display_name=self.display_name,
                is_enabled=self._is_enabled,
                trigger=self.trigger._to_rest_object() if self.trigger is not None else None,
            )
        )

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the asset content into a file in YAML format.

        :param dest: The local path or file stream to write the YAML content to.
            If dest is a file path, a new file will be created.
            If dest is an open file, the file will be written to directly.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        :raises FileExistsError: Raised if dest is a file path and the file already exists.
        :raises IOError: Raised if dest is an open file and the file is not writable.
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        res: dict = MonitorScheduleSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member
        return res

    @classmethod
    def _from_rest_object(cls, obj: RestSchedule) -> "MonitorSchedule":
        properties = obj.properties
        return cls(
            trigger=TriggerBase._from_rest_object(properties.trigger),
            create_monitor=MonitorDefinition._from_rest_object(
                properties.action.monitor_definition, tags=obj.properties.tags
            ),
            name=obj.name,
            id=obj.id,
            display_name=properties.display_name,
            description=properties.description,
            tags=properties.tags,
            properties=properties.properties,
            provisioning_state=properties.provisioning_state,
            is_enabled=properties.is_enabled,
            creation_context=SystemData._from_rest_object(obj.system_data) if obj.system_data else None,
        )

    def _create_default_monitor_definition(self) -> None:
        self.create_monitor._populate_default_signal_information()

    def _set_baseline_data_trailing_tags_for_signal(self, signal_name: str) -> None:
        if self.tags is not None:
            self.tags[f"{signal_name}.baselinedata.datarange.type"] = "Trailing"
            self.tags[f"{signal_name}.baselinedata.datarange.window_size"] = "P7D"
