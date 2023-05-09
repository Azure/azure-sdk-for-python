# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from os import PathLike
from pathlib import Path
from typing import AnyStr, Dict, IO, Optional, Union

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, ScheduleType
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._monitoring.definition import MonitorDefinition
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._schedule.schedule import Schedule
from azure.ai.ml.entities._schedule.trigger import CronTrigger, RecurrenceTrigger, TriggerBase
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._restclient.v2023_04_01_preview.models import CreateMonitorAction
from azure.ai.ml._restclient.v2023_04_01_preview.models import Schedule as RestSchedule
from azure.ai.ml._restclient.v2023_04_01_preview.models import ScheduleProperties
from azure.ai.ml._schema.monitoring.schedule import MonitorScheduleSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import dump_yaml_to_file

module_logger = logging.getLogger(__name__)


@experimental
class MonitorSchedule(Schedule, RestTranslatableMixin):
    """Monitor schedule

    :param name: Name of the schedule.
    :type name: str
    :param trigger: Trigger of the schedule.
    :type trigger: Union[~azure.ai.ml.entities.CronTrigger
        , ~azure.ai.ml.entities.RecurrenceTrigger]
    :param create_monitor: The schedule action monitor definition
    :type create_monitor: ~azure.ai.ml.entities.MonitorDefinition
    :param display_name: Display name of the schedule.
    :type display_name: str
    :param description: Description of the schedule, defaults to None
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The job property dictionary.
    :type properties: dict[str, str]
    """

    def __init__(
        self,
        *,
        name: str,
        trigger: Union[CronTrigger, RecurrenceTrigger],
        create_monitor: MonitorDefinition,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ):
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
        **kwargs,
    ) -> "MonitorSchedule":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return cls(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            **load_from_dict(MonitorScheduleSchema, data, context, **kwargs),
        )

    def _to_rest_object(self) -> RestSchedule:
        return RestSchedule(
            properties=ScheduleProperties(
                description=self.description,
                properties=self.properties,
                tags=self.tags,
                action=CreateMonitorAction(monitor_definition=self.create_monitor._to_rest_object()),
                display_name=self.display_name,
                is_enabled=self._is_enabled,
                trigger=self.trigger._to_rest_object(),
            )
        )

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the schedule content into a file in yaml format.

        :param dest: The destination to receive this schedule's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[str, PathLike, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        return MonitorScheduleSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member

    @classmethod
    def _from_rest_object(cls, obj: RestSchedule) -> "MonitorSchedule":
        properties = obj.properties
        return cls(
            trigger=TriggerBase._from_rest_object(properties.trigger),
            create_monitor=MonitorDefinition._from_rest_object(properties.action.monitor_definition),
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
