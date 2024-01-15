# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import ImportDataAction
from azure.ai.ml._restclient.v2023_04_01_preview.models import Schedule as RestSchedule
from azure.ai.ml._restclient.v2023_04_01_preview.models import ScheduleProperties
from azure.ai.ml._schema._data_import.schedule import ImportDataScheduleSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, ScheduleType
from azure.ai.ml.entities._data_import.data_import import DataImport
from azure.ai.ml.entities._schedule.schedule import Schedule
from azure.ai.ml.entities._schedule.trigger import CronTrigger, RecurrenceTrigger, TriggerBase
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict


@experimental
class ImportDataSchedule(Schedule):
    """ImportDataSchedule object.

    :param name: Name of the schedule.
    :type name: str
    :param trigger: Trigger of the schedule.
    :type trigger: Union[CronTrigger, RecurrenceTrigger]
    :param import_data: The schedule action data import definition.
    :type import_data: DataImport
    :param display_name: Display name of the schedule.
    :type display_name: str
    :param description: Description of the schedule, defaults to None
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The data import property dictionary.
    :type properties: dict[str, str]
    """

    def __init__(
        self,
        *,
        name: str,
        trigger: Optional[Union[CronTrigger, RecurrenceTrigger]],
        import_data: DataImport,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
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
        self.import_data = import_data
        self._type = ScheduleType.DATA_IMPORT

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "ImportDataSchedule":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return ImportDataSchedule(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            **load_from_dict(ImportDataScheduleSchema, data, context, **kwargs),
        )

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> ImportDataScheduleSchema:
        return ImportDataScheduleSchema(context=context)

    @classmethod
    def _from_rest_object(cls, obj: RestSchedule) -> "ImportDataSchedule":
        return cls(
            trigger=TriggerBase._from_rest_object(obj.properties.trigger),
            import_data=DataImport._from_rest_object(obj.properties.action.data_import_definition),
            name=obj.name,
            display_name=obj.properties.display_name,
            description=obj.properties.description,
            tags=obj.properties.tags,
            properties=obj.properties.properties,
            provisioning_state=obj.properties.provisioning_state,
            is_enabled=obj.properties.is_enabled,
            creation_context=SystemData._from_rest_object(obj.system_data),
        )

    def _to_rest_object(self) -> RestSchedule:
        return RestSchedule(
            properties=ScheduleProperties(
                description=self.description,
                properties=self.properties,
                tags=self.tags,
                action=ImportDataAction(data_import_definition=self.import_data._to_rest_object()),
                display_name=self.display_name,
                is_enabled=self._is_enabled,
                trigger=self.trigger._to_rest_object() if self.trigger is not None else None,
            )
        )
