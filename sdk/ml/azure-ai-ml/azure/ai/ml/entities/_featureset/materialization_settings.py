# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    MaterializationSettings as RestMaterializationSettings,
    MaterializationStoreType,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities import JobSchedule, NotificationConfiguration, MaterializationComputeResource
from azure.ai.ml._utils._experimental import experimental


@experimental
class MaterializationSettings(RestTranslatableMixin):
    def __init__(
        self,
        *,
        schedule: JobSchedule,
        offline_enabled: Optional[bool],
        online_enabled: Optional[bool],
        notification: Optional[NotificationConfiguration],
        resources: Optional[MaterializationComputeResource],
        spark_conf: Optional[Dict[str, str]],
        **kwargs
    ):
        self.schedule = schedule
        self.offline_enabled = offline_enabled
        self.online_enabled = online_enabled
        self.notification = notification
        self.resources = resources
        self.spark_conf = spark_conf

    def _to_rest_object(self) -> RestMaterializationSettings:
        store_type = None
        if self.offline_enabled and self.online_enabled:
            store_type = MaterializationStoreType.ONLINE_AND_OFFLINE
        elif self.offline_enabled:
            store_type = MaterializationStoreType.OFFLINE
        elif self.online_enabled:
            store_type = MaterializationStoreType.ONLINE
        else:
            store_type = MaterializationStoreType.NONE

        return RestMaterializationSettings(
            schedule=self.schedule._to_rest_object(),
            notification=self.notification._to_rest_object() if self.notification else None,
            resource=self.resources._to_rest_object() if self.resources else None,
            spark_configuration=self.spark_conf,
            store_type=store_type,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMaterializationSettings) -> "MaterializationSettings":
        if not obj:
            return None
        return MaterializationSettings(
            schedule=JobSchedule._from_rest_object(obj.schedule),
            notification=NotificationConfiguration._from_rest_object(obj.notification),
            resources=MaterializationComputeResource._from_rest_object(obj.resources),
            spark_conf=obj.spark_configuration,
            offline_enabled=obj.store_type == MaterializationStoreType.OFFLINE,
            online_enabled=obj.store_type == MaterializationStoreType.ONLINE,
        )
