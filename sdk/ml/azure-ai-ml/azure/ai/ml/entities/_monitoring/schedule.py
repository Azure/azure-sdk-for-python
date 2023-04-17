# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, ScheduleType
from azure.ai.ml.entities._monitoring.definition import MonitorDefinition
from azure.ai.ml.entities._schedule.schedule import Schedule
from azure.ai.ml.entities._schedule.trigger import CronTrigger, RecurrenceTrigger
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._schema.monitoring.schedule import MonitorScheduleSchema
from azure.ai.ml._utils._experimental import experimental

module_logger = logging.getLogger(__name__)


@experimental
class MonitorSchedule(Schedule):
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
