# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
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

module_logger = logging.getLogger(__name__)


@experimental
class MonitorSchedule(Schedule, RestTranslatableMixin):
    def __init__(
        self,
        *,
        name: str,
        trigger: Union[CronTrigger, RecurrenceTrigger],
        create_monitor: MonitorDefinition = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ):
        kwargs.pop("create_job", None)
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

    @property
    def create_job(self):
        module_logger.warning("create_job is not a valid property of MonitorSchedule")

    @create_job.setter
    def create_job(self, value):  # pylint: disable=unused-argument
        module_logger.warning("create_job is not a valid property of MonitorSchedule")

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

    @classmethod
    def _from_rest_object(cls, obj: RestSchedule) -> "MonitorSchedule":
        properties = obj.properties
        return cls(
            trigger=TriggerBase._from_rest_object(properties.trigger),
            create_monitor=MonitorDefinition._from_rest_object(properties.action.monitor_definition),
            name=obj.name,
            display_name=properties.display_name,
            description=properties.description,
            tags=properties.tags,
            properties=properties.properties,
            provisioning_state=properties.provisioning_state,
            is_enabled=properties.is_enabled,
            creation_context=SystemData._from_rest_object(obj.system_data),
        )
